# !/bin/sh
# the next line restarts using tclsh \
exec tclsh "$0" "$@"	

#//#
#	This program creates input files for other programs using Ulyxes TclAPI.
#       .tca, .geo and .coo files can be created, from the manually measured 
#	points. 
#	.geo and .coo formats are used by GeoEasy
#	@param output name of output file
#	@param atr 0/1 measure without/with ATR, optional (default 1)
#	@param com name of RS-232 parameter file, optional (default leica.com)
#	@param debuglevel 0/1/2 for debugging, optional (default 0)
#	
#	<p>Ulyses - an open source project to drive total stations and
#			publish observation results</p>
#	<p>GPL v2.0 license</p>
#	<p>Copyright (C) 2010-2012 Zoltan Siki <siki@agt.bme.hu></p>
#	@author Daniel Moka & Zoltan Siki
#	@version 1.1
#//#

source global.tcl
source common.tcl
source leica.tcl

global argv argc

if {$argc == 0} {
	puts "usage: fileMaker.tcl output_file <param_file>"
	return
}
set fn [lindex $argv 0]
switch -exact [file extension $fn]  {
	".geo" { set fgeo $fn
		set fcoo "[file rootname $fn].coo"
	}
	".coo" { set fcoo $fn }
	".tca" { set ftca $fn }
}
if {[info exists fgeo]} {
	if {[catch {set fgeo [open $fgeo "w"]} msg]} {
		puts stderr "Error opening output file: $fgeo"
		exit 1
	}
}
if {[info exists fcoo]} {
	if {[catch {set fcoo [open $fcoo "w"]} msg]} {
		puts stderr "Error opening output file: $fcoo"
		exit 1
	}
}
if {[info exists ftca]} {
	if {[catch {set ftca [open $ftca "w"]} msg]} {
		puts stderr "Error opening output file: $ftca"
		exit 1
	}
}
# set station name & save to file
if {[info exists fgeo] || [info exists ftca]} {
	puts stdout "Station name:"
	set stid [gets stdin]
	if {[info exists fgeo]} {
		puts $fgeo "{2 $stid} {3 0}"
	}
	if {[info exists ftca]} {
		puts $ftca "!,$stid,0"
	}
}
set atr 1
if {$argc > 1} { set atr [lindex $argv 1] }

set com "leica.com"
if {$argc > 2} { set com [lindex $argv 2] }

set debuglevel 0
if {$argc > 3} { set debuglevel [lindex $argv 3] }

# open and set up communication port
if {[OpenCom $com]} {
	puts "Error opening communication port"
	exit 1
}

if {[info exists fgeo]} {	;# get station coords
	puts stdout "Station Easting:"
	set ste [gets stdin]
	puts stdout "Station Northing:"
	set stn [gets stdin]
	puts stdout "Station Elevation:"
	set stz [gets stdin]
	if {[string length $ste] && [string length $stn] && [string length $stz]} {
		puts $fcoo "{5 $stid} {38 $ste} {37 $stn} {39 $stz}"
		SetStation $ste $stn $stz
	} else {
		SetStation 0 0 0
	}
}
SetATR 1
while {1} {
	puts stdout "Target name:"
	set id [gets stdin]
	if {[string length $id] == 0} {
		catch { close $fgeo }
		catch { close $fcoo }
		catch { close $ftca }
		break 
	}
	if {$atr} {
		# find target prism at actual direction
		MoveRel 0 0 "RAD" $atr
	}
	set res [Measure]
	if {[llength $res]} {
		if {[info exists fgeo]} {
			puts $fgeo "{5 $id} {112 1} $res"
		}
		if {[info exist ftca]} {
			puts $ftca "$id,[string trim [DMS [GetVal 7 $res]]],[string trim [DMS [GetVal 8 $res]]],[format "%.4f" [GetVal 9 $res]],1,$atr"
		}
		if {[info exists fcoo]} {
			set res [Coords]
			if {[llength $res]} { puts $fcoo "{5 $id} $res" }
		}
	}
}
