#!/bin/sh
# the next line restarts using tclsh \
exec tclsh "$0" "$@"
#******************************************************************************
#	Ulyses - an open source project to drive total stations and
#			publish observation results
#	GPL v2.0 license
#	Copyright (C) 2010-2012 Zoltan Siki <siki@agt.bme.hu>
#******************************************************************************
# Sample tcl script to find prism
#******************************************************************************
source global.tcl
source common.tcl
source leica.tcl

global env argv argc
global coo
set usage "Usage search.tcl station coo_file \[com_file\]"

if {$argc == 1 && [lindex $argv 0] == "-h"} {
	puts $usage
	return
}

if {$argc < 2 } {
	puts $usage
	return
}
set w [LoadCoo [lindex $argv 1] ] 
if {$w != 0} {
	puts "Error in input file, line: $w"
	return
}
set stat [lindex $argv 0]
if {[info exists coo($stat)] == 0} {
	puts "Station not found in coordinate file"
	return
}

set debuglevel 2
set hz_min 0
set hz_max $PI2
set dm 1.5	;# Height torelance for search (+- 1.5m)

# search at step degrees

set step [expr {3.0 / 180.0 * $PI}]

# open and set communication port
set com "leica.com"
if {$argc > 2} {
	set com [lindex $argv 2]
}
if {[OpenCom $com]} {
	puts "Error opening communication port"
	exit 1
}

# search prism 
foreach pn [array names coo] {
	if {$stat == $pn} { continue }
	set dist [Distance [GetVal 37 $coo($stat)] [GetVal 38 $coo($stat)] [GetVal 37 $coo($pn)] [GetVal 38 $coo($pn)]]
	set dh [expr {[GetVal 39 $coo($pn)] - [GetVal 39 $coo($stat)]}]
	set v_min [expr {atan2($dist,($dh + $dm))}]
	set v_max [expr {atan2($dist,($dh - $dm))}]
	set hz $hz_min
	set found 0
	while {$hz < $hz_max && $found == 0} {
puts "hz: [DMS $hz]"
		set v $v_min
		while {$v < $v_max && $found == 0} {
puts "v: [DMS $v]"
			if {[Move $hz $v "RAD" 1] == 0} {
				set found 1
				puts "Prism found at $hz $v"
			}
			if {$found == 0} {
				set v [expr {$v + $step}]
			}
		}
		if {$found == 0} {
			set hz [expr {$hz + $step}]
		}
	}
	if {$found == 1} {break}
}
if {$found == 1} {


}
CloseCom
