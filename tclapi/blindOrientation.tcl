#!/bin/sh
# the next line restarts using tclsh \
exec tclsh "$0" "$@"
#//#
#	This program search for a prism and set up orientation
#	@param station station name in coordinate list
#	@param coo_file coordinate list in GeoEasy form
#
#	<p>Ulyses - an open source project to drive total stations and
#			publish observation results</p>
#	<p>GPL v2.0 license</p>
#	<p>Copyright (C) 2010-2012 Zoltan Siki <siki@agt.bme.hu></p>
#	@author Daniel Moka
#	@author Zoltan Siki
#	@version 1.0

source global.tcl
source common.tcl
source leica.tcl

global argv argc
global coo
global PI2
set usage "Usage blindOrientation.tcl station coo_file <com_file> <debuglevel>"

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

# open and set communication port
set compar "leica.com"
if {$argc > 2} {
	set compar [lindex $argv 2]
}
OpenCom $compar

set debuglevel 0
if {$argc > 3} {
	set debuglevel [lindex $argv 3]
}

set dm 0.5	;# Height torelance for search (+-)

# search at step degrees
set step [expr {3.0 / 180.0 * $PI}]

# set EDM mode & ATR
SetEDMMode 2
SetATR 1

set dhz 0
set vmin_limit [expr {30.0 / 180.0 * $PI}]
set vmax_limit [expr {125.0 / 180.0 * $PI}]
set vma $vmin_limit
set vmi $vmax_limit
# calculate distances and vertical directions
foreach pn [array names coo] {
	if {$stat == $pn} { continue }
	set dist($pn) [Distance [GetVal 37 $coo($stat)] [GetVal 38 $coo($stat)] [GetVal 37 $coo($pn)] [GetVal 38 $coo($pn)]]
	set dh [expr {[GetVal 39 $coo($pn)] - [GetVal 39 $coo($stat)]}]
	set v_min($pn) [expr {atan2($dist($pn), $dh + $dm)}]
	set v_max($pn) [expr {atan2($dist($pn), $dh - $dm)}]
	if {$v_min($pn) < $vmi} { set vmi $v_min($pn) }
	if {$v_max($pn) > $vma} { set vma $v_max($pn) }
}
if {$vmi < $vmin_limit} { set vmi $vmin_limit }
if {$vma > $vmax_limit} { set vma $vmax_limit }

# search prism
set found 0
while {$dhz < $PI2 && ! $found} {
	set angles [GetAngles]
	set actHz [GetVal 7 $angles]
	set actV [GetVal 8 $angles]
	if {$debuglevel} { puts "actHz: [DMS $actHz]" }
	set hz $actHz
	set v $actV
# TODO repeated code from the while loop!!!!
	if {[Move $hz $v "RAD" 1] == 0} {
		set lp [Measure]
		if {[llength $lp] > 2} {
			set hd [expr {[GetVal 9 $lp] * sin([GetVal 8 $lp])}]
			foreach pn [array names dist] {
				if {[expr {abs($dist($pn) - $hd)}] < 0.5 && \
					$v > $v_min($pn) && $v < $v_max($pn)} {
					set found 1
					if {$debuglevel} { puts "Point $pn found at $hz $v $dist($pn)" }
					break
				}
			}
		}
	}
	if {$found} { break}
	set v $vmi
	while {$v < $vma && ! $found} {
		if {$debuglevel} { puts "actV: [DMS $v]" }
		if {[Move $hz $v "RAD" 1] == 0} {
			set lp [Measure]
			if {[llength $lp] > 2} {
				set hd [expr {[GetVal 9 $lp] * sin([GetVal 8 $lp])}]
				foreach pn [array names dist] {
					if {[expr {abs($dist($pn) - $hd)}] < 0.5 && \
						$v > $v_min($pn) && $v < $v_max($pn)} {
						set found 1
						if {$debuglevel} { puts "Point $pn found at $hz $v $dist($pn)" }
						break
					}
				}
			}
		}
		if {$found} { break }
		set v [expr {$v + $step}]
	}
	if {$found} { break }
	MoveRel $step 0 "RAD" 0	;# rotate instument horizontally
	set dhz [expr {$dhz + $step}]
}

if {$found} {
	if {$debuglevel} { puts "Orientation set" }
	set bearAn [Bearing [GetVal 38 $coo($stat)] [GetVal 37 $coo($stat)] [GetVal 38 $coo($pn)] [GetVal 37 $coo($pn)]]
	SetOri $bearAn
}
CloseCom
