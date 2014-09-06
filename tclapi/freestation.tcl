#!/bin/sh
# the next line restarts using tclsh \
exec tclsh "$0" "$@"
#//#
#	This program measures to given directions and calculates free station
#	using GNU GaMa, finally upload station coordinmates and orientation to
#	the total station
#	@param input_file directions to points (tca or geo file format)
#	@param com name of RS-232 parameter file, optional (default leica.com)
#	@param debuglevel 0/1/2 for debugging, optional (default 0)
#
#	<p>Ulyses - an open source project to drive total stations and
#			publish observation results</p>
#	<p>GPL v2.0 license</p>
#	<p>Copyright (C) 2010-2012 Zoltan Siki <siki@agt.bme.hu></p>
#	@author Zoltan Siki
#	@version 1.0
#//#

source global.tcl
source common.tcl
source leica.tcl
source gamaxml.tcl

package require http
#	make measurement from a geo array
#	@param geo name of geo array in memory
#	@param atr 0/1 without ATR/with ATR
proc FreeStation {geo {atr 1} {edmMode 2}} {
	global PI PI2 maxtry
	global fp
	if {[GetEDMMode] != $edmMode} { SetEDMMode $edmMode }
	upvar #0 $geo g
	if {[GetVal 2 $g(0)] != ""} {
		set first 1	;# skip station record
	} else {
		set first 0
	}
	set last [expr {[array size g] - 1}]
	# get max number of faces
	set max 0
	for {set i $first} {$i <= $last} {incr i} {
		set m [GetVal 112 $g($i)]
		if {$m > $max} { set max $m}
	}
# TODO actually 1 face can be used
set max 1
	set n 0	;# number of faces measured
	while {$n < $max} {
		if {[expr {$n % 2}] == 0} {	;# face left
			set i1 $first
			set i2 [expr {$last + 1}]
			set i3 1
		} else {			;# face right
			set i1 $last
			set i2 [expr {$first - 1}]
			set i3 -1
		}
		for {set i $i1} {$i != $i2} {incr i $i3} {
			if {[GetVal 112 $g($i)] > $n} {
				set pn [GetVal 5 $g($i)]
				set hz [GetVal 7 $g($i)]
				set v [GetVal 8 $g($i)]
				if {$i3 == -1} {
					# change angles to face right
					set hz [expr {$hz - $PI}]
					while {$hz < 0} {set hz [expr {$hz + $PI2}]}
					set v [expr {$PI2 - $v}]
				}
				# rotate instrument
				set res ""
				set j 0
				while {$j < $maxtry} {		;# try measurement several times
					if {[set res [Move $hz $v "RAD" $atr]] == 0} {	;# rotate instrument
						if {[llength [set res [Measure]]] > 1} {	;# measure dist
							set hz1 [Rad2Gon [GetVal 7 $res]]
							set z1 [Rad2Gon [GetVal 8 $res]]
							set d1 [GetVal 9 $res]
							puts $fp "<direction to=\"$pn\" val=\"$hz1\" stdev=\"1\" />"
							puts $fp "<z-angle to=\"$pn\" val=\"$z1\" from_dh=\"0.0\" to_dh=\"0.0\" stdev=\"1\" />"
							puts $fp "<s-distance to=\"$pn\" val=\"$d1\" from_dh=\"0.0\" to_dh=\"0.0\" stdev=\"1\" />"
							break	;# leave while
						}
					}
					incr j
					after 5000	;# wait before retry
				}
			}
		}
		incr n
	}
}

global argv argc
global geo
global coo

if {$argc == 0} {
	puts "Usage freestation.tcl input_file <com_file> <debuglevel>"
	exit 1
}

# read measurement file
set in [lindex $argv 0]
if {[string tolower [file extension $in]] == ".geo"} {
	if {[LoadGeo $in]} {
		puts "error in input file"
		exit 1
	}
	# get coords if available
	set c "[file rootname $in].coo"
	if {[file exists $c]} {
		if {[LoadCoo $c]} {
			puts "error loading coordinates"
			exit 1
		}
	}
}

# get station id
global stn stnx stny stnz
set stn [GetVal 2 $geo(0)]
set stnx 0
set stny 0
set stnz 0
if {[string length $stn]} {
	if {[info exists coo($stn)]} {
		set stnx [GetVal 37 $coo($stn)]
		set stny [GetVal 38 $coo($stn)]
		set stnz [GetVal 39 $coo($stn)]
	}
}
# open GNU Gama XML
global fp
set fp [open "tmp.xml" "w"]
# write header
puts $fp "<?xml version=\"1.0\" ?>"
puts $fp "<!DOCTYPE gama-xml SYSTEM \"gama-xml.dtd\">"
puts $fp "<gama-local version=\"2.0\">"
puts $fp "<network axes-xy=\"ne\" angles=\"right-handed\">"
puts $fp "<description>"
puts $fp "Ulyxes freestation"
puts $fp "</description>"
puts $fp "<parameters sigma-apr = \"1\" conf-pr = \"0.99\" tol-abs = \"1000\" sigma-act = \"aposteriori\" update-constrained-coordinates=\"yes\" />"
puts $fp "<points-observations distance-stdev=\"1.0 1.0 0.0\" direction-stdev=\"1\" angle-stdev=\"2\">"

foreach pn [array names coo] {
	set x [GetVal 37 $coo($pn)]
	set y [GetVal 38 $coo($pn)]
	set z [GetVal 39 $coo($pn)]
	if {$pn == $stn} {
		puts $fp "<point id=\"$pn\" y=\"$y\" x=\"$x\" z=\"$z\" adj=\"xyz\" />"
	} else {
		puts $fp "<point id=\"$pn\" y=\"$y\" x=\"$x\" z=\"$z\" fix=\"xyz\" />"
	}
}


set atr 1	;# default with ATR
set edmMode 2
# open and set communication port
set com "leica.com"
if {$argc > 1} {
	set com [lindex $argv 3]
}
if {[OpenCom $com]} {
	puts "Error opening communication port"
	exit 1
}
set debuglevel 0
if {$argc > 2} {
	set debuglevel [lindex $argv 4]
}

SetATR $atr
SetStation $stny $stnx $stnz
# start measurement program
puts $fp "<obs from=\"$stn\">"
FreeStation "geo" $atr $edmMode
puts $fp "</obs>"
puts $fp "</points-observations>"
puts $fp "</network>"
puts $fp "</gama-local>"
close  $fp
# start gama adjustment
if {[catch {eval [concat exec "./gama-local --angles 360 --xml res.xml --text res.txt tmp.xml"]} msg]} {
	puts $msg
	return
}
# process results
set f [open "res.xml" "r"]
set xmllist [xml2list [read $f]]
close $f
ProcessList $xmllist
# set station coords from global variables
SetStation $stny $stnx $stnz
# set orientation from global variable
set hz [expr {[GetVal 7 [GetAngles]] + [Gon2Rad $oa]}]
SetOri $hz
catch {file delete "res.xml"}
catch {file delete "res.txt"}
catch {file delete "tmp.xml"}

set t [clock format [clock seconds] -format {%Y-%m-%d+%H:%M:%S}]
set token [http::geturl "http://localhost/server_scripts/sensor2server.php?pn=$stn&epoch=$t&e=$stny&n=$stnx&z=$stnz"]
upvar #0 $token state
if {$state(body) != "0"} {
	puts "Error: $state(body)"
}
CloseCom
