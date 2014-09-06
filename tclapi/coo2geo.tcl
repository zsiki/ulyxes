#!/bin/sh
# the next line restarts using tclsh \
exec tclsh "$0" "$@"
#//#
#	This program creates (writes to the standard output)
#	input file for robot.tcl from points at given coordinates
#	@param station station name in coordinate list
#	@param coo_file coordinate list in GeoEasy form
#	@param faces faces to measure
#	@param debuglevel
#
#	<p>Ulyses - an open source project to drive total stations and
#			publish observation results</p>
#	<p>GPL v2.0 license</p>
#	<p>Copyright (C) 2013 Zoltan Siki <siki@agt.bme.hu></p>
#	@author Zoltan Siki
#	@version 1.0
#//#

source global.tcl
source common.tcl

global argv argc
global coo
set usage "Usage coo2geo.tcl station coo_file <faces> <debuglevel>"

if {$argc < 2 } {
	puts $usage
	return
}
if {[LoadCoo [lindex $argv 1]]} {
	puts "Error in input file, line: $w"
	exit 1
}
set stat [lindex $argv 0]
if {[info exists coo($stat)] == 0} {
	puts "Station not found in coordinate file"
	exit 1
}

set faces 1
if {$argc > 2} {
	set faces [lindex $argv 2]
}

set debuglevel 0
if {$argc > 3} {
	set debuglevel [lindex $argv 3]
}

# calculate bearings and zenith angles
puts "{2 $stat} {3 0}"
foreach pn [array names coo] {
	if {$stat == $pn} { continue }
	set dist [Distance [GetVal 38 $coo($stat)] [GetVal 37 $coo($stat)] [GetVal 38 $coo($pn)] [GetVal 37 $coo($pn)]]
	set bear [Bearing [GetVal 38 $coo($stat)] [GetVal 37 $coo($stat)] [GetVal 38 $coo($pn)] [GetVal 37 $coo($pn)]]
	set dh [expr {[GetVal 39 $coo($pn)] - [GetVal 39 $coo($stat)]}]
	set za [expr {atan2($dist, $dh)}]
	puts "{5 $pn} {7 $bear} {8 $za} {11 $dist} {112 $faces}"
}
