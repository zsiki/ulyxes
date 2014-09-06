#!/bin/sh
# the next line restarts using tclsh \
exec tclsh "$0" "$@"
#//#
#	This program measures to given directions
#	@param input_file directions to points (tca file format)
#	@param atr 0/1 measure with no reflector/with reflector, optional (default 1)
#	@param edmMode distance measurement mode, optional (default 2)
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

package require http
#	Read measurement program from tca file
#
#	<p>tca file format:<br>
#	!,station_id,ih (optional)<br>
#	point_id,hz,v,faces,PC<br>
#		faces = 0 no measurement, 1 measure face left, 2 measure two faces, 4 measure two rounds<br>
#		PC prism constant [mm], optional if missing no change to the measured distance
#	@param fn path to tca file to load
#	@return row number in case of error or 0 if file loaded
proc LoadTca {fn} {
	global reg
	global geo	;# GeoEasy like fieldbook

	# open input file
	if {[catch {set f1 [open $fn r]}] != 0} {
		return -6
	}
	# get name part from path
	catch "unset geo"	;# clear previous data
	set lineno 0		;# line numbers in input file
	while {! [eof $f1]} {
		gets $f1 ibuf
		if {[string length [string trim $ibuf]] == 0} {continue}
		set buflist [split $ibuf ","]
		if {[lindex $buflist 0] == "!"} {
			# station
			set buf [list [list 2 [lindex $buflist 1]]]
			if {[llength $buflist] > 2} {
				lappend buf [list 3 [lindex $buflist 2]]
			}
		} else {
			# observation
			set buf [list [list 5 [lindex $buflist 0]]]
			lappend buf [list 7 [lindex $buflist 1]]
			lappend buf [list 8 [lindex $buflist 2]]
			lappend buf [list 9 [lindex $buflist 3]]
			lappend buf [list 112 [lindex $buflist 4]]
			if {[llength $buflist] > 5} {
				lappend buf [list 20 [lindex $buflist 5]]
			}
		}
		# check for DMS angles (DDD-MM-SS format)
		foreach code {7 8} {
			if {[set w [GetVal $code $buf]] != "" && \
				[regexp $reg(3) $w]} {
				set buf [DelVal $code $buf]
				set tmp [DMS2Rad $w]
				if {[string length $w] > 0} {
					lappend buf [list $code $tmp]
				} else { 	;# invalid angle value
					catch {close $f1}
					return [expr {$lineno + 1}]	
				}
			}
		}
		# check for numeric values
		foreach code {3 7 8 9 20 112} {
			if {[set w [GetVal $code $buf]] != ""} {
				if {[regexp $reg(2) $w] == 0} {
					catch {close $f1}
					return [expr {$lineno + 1}]	
				}
			}
		}
		set geo($lineno) $buf
		incr lineno
	}
	return 0
}

#	make measurement from a geo array
#	@param geo name of geo array in memory
#	@param atr 0/1 without ATR/with ATR
proc Robot {geom {atr 1} {edmMode 2}} {
	global PI PI2 maxtry
	if {[GetEDMMode] != $edmMode} { SetEDMMode $edmMode }
	upvar #0 $geom g
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
	set n 0	;# number of faces measured
	while {$n < $max} {
		if {[expr {$n % 2}] == 0} { ;# face left
			set i1 $first
			set i2 [expr {$last + 1}]
			set i3 1
		} else {					;# face right
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
							if {[llength [set res [Coords]]] > 1} {	;# get coords
								if {[info exists c($pn)]} {
									set nn [GetVal 112 $c($pn)]	;# repeat count sofar
									set nn1 [expr {$nn + 1}]
									set east  [expr {([GetVal 38 $c($pn)] * $nn + [GetVal 38 $res]) / $nn1}]
									set north [expr {([GetVal 37 $c($pn)] * $nn + [GetVal 37 $res]) / $nn1}]
									set elev  [expr {([GetVal 39 $c($pn)] * $nn + [GetVal 39 $res]) / $nn1}]
									set res [list [list 38 $east] [list 37 $north] [list 39 $elev] [list 112 $nn1]]
									set c($pn) $res
									break	;# leave while
								} else {
									lappend res [list 112 1]	;# repeat count
									set c($pn) $res
									break	;# leave while
								}
							}
						}
					}
					incr j
					after 5000	;# wait before retry
				}
			}
		}
		incr n
	}
	# create SQL commands
	set t [clock format [clock seconds] -format {%Y-%m-%d+%H:%M:%S}]
	foreach pn [lsort -dictionary [array names c]] {
		set e [GetVal 38 $c($pn)]
		set n [GetVal 37 $c($pn)]
		set z [GetVal 39 $c($pn)]
		# TODO change localhost to parameter
		set token [http::geturl "http://localhost/server_scripts/sensor2server.php?pn=$pn&epoch=$t&e=$e&n=$n&z=$z"]
		upvar #0 $token state
		if {$state(body) != "0"} {
			puts "Error: $state(body)"
		}
		puts "$pn;$e;$n;$z;$t"
	}
}

global argv argc
global geo
global coo

if {$argc == 0} {
	puts "Usage robot.tcl input_file <atr> <com_file> <debuglevel>"
	exit 1
}

# read measurement file
set in [lindex $argv 0]
if {[string tolower [file extension $in]] == ".tca"} {
		if {[LoadTca $in]} {
			puts "error in input file"
			exit 1
		}
} elseif {[string tolower [file extension $in]] == ".geo"} {
		if {[LoadGeo $in]} {
			puts "error in input file"
			exit 1
		}
}

# get coords if available
set c "[file rootname $in].coo"
if {[file exists $c]} {
	if {[LoadCoo $c]} {
		puts "error loading coordinates"
		exit 1
	}
}

# get station id
set stn [GetVal 2 $geo(0)]
set stnx 0
set stny 0
set stnz 0
if {[string length $stn]} {
	if {[info exists coo($stn)]} {
		set stnx [GetVal 37 $coo($stn)]
		set stny [GetVal 38 $coo($stn)]
		set stnz [GetVal 39 $coo($stn)]
		if {[string length $stnx] && [string length $stny] &&
			[string length $stnz]} {
		}
	}
}

set atr 1	;# default with ATR
if {$argc > 1} {
	set atr [lindex $argv 1]
}
set edmMode 2
if {$argc > 2} {
	set edmMode [lindex $argv 2]
}
# open and set communication port
set com "leica.com"
if {$argc > 3} {
	set com [lindex $argv 3]
}
if {[OpenCom $com]} {
	puts "Error opening communication port"
	exit 1
}
set debuglevel 0
if {$argc > 4} {
	set debuglevel [lindex $argv 4]
}

SetATR $atr
SetStation $stny $stnx $stnz
# start measurement program
Robot "geo" $atr $edmMode
CloseCom
