# !/bin/sh
# the next line restarts using tclsh \
exec tclsh "$0" "$@"

#//#
#	This program measures a slowly moving prism (with ATR) or 
#	any target at the same direction (without ATR)
#	and writes the time and the measured values to standard output.
#	Oriented total station is supposed.
#
#	@param atr 0/1/2/3/4 measure without/with ATR/with ATR but no distance meas/lock single distance measurement/lock with distances  (default 1)
#	@param mode EDM mode (default 0)
#	@param com name of RS-232 dt file optional (default leica.com)
#	@param debuglevel 0/1/2 for debugging, optional (default 0)
#	
#	<p>Ulyses - an open source project to drive total stations and
#			publish observation results</p>
#	<p>GPL v2.0 license</p>
#	<p>Copyright (C) 2010-2012 Zoltan Siki <siki@agt.bme.hu></p>
#	@author Daniel Moka
#	@version 1.1
#//#

source global.tcl
source common.tcl
source leica.tcl

global argv argc

# Adding parameter  0/1 =  measuring without distance(only angles) / measuring angles and distances too
set dist 1	;# default with distances
if {$argc > 0} { set dist [lindex $argv 0] }

# Adding the 2nd parameter
set mode 0
if {$argc > 1} {set mode [lindex $argv 1]}

# Adding the 3nd parameter
set com "leica.com"
if {$argc > 2} {set com [lindex $argv 2]}

set debuglevel 0
if {$argc > 3} { set debuglevel [lindex $argv 3] }

# Open and set communication port
if {[OpenCom $com]} {
	puts "Error opening communication port"
	exit 1
}
if {$dist} {
	SetEDMMode $mode	;# distance measurement mode
	SetLock 0			;# turn off lock
	SetATR 1			;# set automatic target recognition
	MoveRel 0 0 "RAD" 1	;# target on prism with ATR
	set res [Measure]	;# initial measurement
	set systemTime [clock seconds]  ;# set current time
	if {[llength $res] > 2} {
		set sd [GetVal 9 $res]	;# initial slope distance
		puts "[DMS [GetVal 7 $res]] [DMS [GetVal 8 $res]] [GetVal 9 $res] [clock format $systemTime -format %H:%M:%S]"
	} else {
		puts "*** $res [clock format $systemTime -format %H:%M:%S]"
	}
	if {$dist == 3 || $dist == 4} {
		SetLock 1	;# lock on target
		LockIn
#		MoveRel 0 0 "RAD" 1	;# target on prism with ATR
#		TODO FineAdjust????
	}
} else {
	SetATR 0
	SetEDMMode $mode
}

while {1} {
	set systemTime [clock seconds]  ;# set current time
	switch -exact $dist {
		0 {
			set res [Measure]	;# distance measurement
		}
		1 {
			MoveRel 0 0 "RAD" 1	;# aim on target with ATR
			set res [Measure]	;# distance measurement
		}
		2 {
			MoveRel 0 0 "RAD" 1	;# aim on target with ATR
			set res [GetAngles]	;# get angles only
		}
		3 {
			set res [GetAngles]	;# get angles only during lock
		}
		4 {
			set res [Measure]	;# distance measurement during lock
		}
	}
	# write data to standard output
	if {[llength $res] >= 2} {
		if {[GetVal 9 $res] == ""} {
			set sd [GetVal 9 $res]
		}
		set dy [format "%10.4f" [expr {$sd * sin([GetVal 8 $res]) * sin([GetVal 7 $res])}]]
		set dx [format "%10.4f" [expr {$sd * sin([GetVal 8 $res]) * cos([GetVal 7 $res])}]]
		puts "$dy $dx [DMS [GetVal 7 $res]] [DMS [GetVal 8 $res]] [format "%10.4f" [GetVal 9 $res]] [clock format $systemTime -format %H:%M:%S]"
	} else {
		puts "*** $res [clock format $systemTime -format %H:%M:%S]"
	}
}
