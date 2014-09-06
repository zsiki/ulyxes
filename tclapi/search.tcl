#!/bin/sh
# the next line restarts using tclsh \
exec tclsh "$0" "$@"
#******************************************************************************
#	Ulyses - an open source project to drive total stations and
#			publish observation results
#	GPL v2.0 license
#	Copyright (C) 2010-2012 Zoltan Siki <siki@agt.bme.hu>
#******************************************************************************
# Sample tcl script to find pism
# parameters: 
#	maxStep - max steps from centre
#	step - angle step in radians (optional)
#	com_file - serial communication parameters in file (optional)
#******************************************************************************

source global.tcl
source common.tcl
source leica.tcl

global env argv argc

if {$argc < 1} {
	puts "Usage: search1.tcl max \[step\] \[com_file\]"
	CloseCom
	return
}

set debuglevel 0
set maxStep [lindex $argv 0]
# search at step degrees
if {$argc < 2} {
	set step 0.024
} else {
	set step [lindex $argv 0]
}

# open and set communication port
if {$argc < 3} {
	OpenCom
} else {
	OpenCom [lindex $argv 2]
} 
if {[MoveRel 0 0 RAD 1] == 0} {
	puts "prism found [GetAngles]"
	CloseCom
	return
}
for {set i 1} {$i < $maxStep} {incr i} {
	if {[expr {$i % 2}] == 1} {
		# odd value move up and left
		# move up
		for {set j 1} {$j <= $i} {incr j} {
DisplayAngles [GetAngles] DMS
			if {[MoveRel 0 -$step RAD 1] == 0} {
				puts "prism found [GetAngles]"
				CloseCom
				return
			}
		}
		# move left
		for {set j 1} {$j <= $i} {incr j} {
DisplayAngles [GetAngles] DMS
			if {[MoveRel -$step 0 RAD 1] == 0} {
				puts "prism found [GetAngles]"
				CloseCom
				return
			}
		}
	} else {
		# even value move down and right
		#move down
		for {set j 1} {$j <= $i} {incr j} {
DisplayAngles [GetAngles] DMS
			if {[MoveRel 0 $step RAD 1] == 0} {
				puts "prism found [GetAngles]"
				CloseCom
				return
			}
		}
		# move left
		for {set j 1} {$j <= $i} {incr j} {
DisplayAngles [GetAngles] DMS
			if {[MoveRel $step 0 RAD 1] == 0} {
				puts "prism found [GetAngles]"
				CloseCom
				return
			}
		}
	}
}
puts "No prism found :("
CloseCom
