#!/bin/sh
# the next line restarts using tclsh \
exec tclsh "$0" "$@"
#//#
# dna03 test program to read staff continuously
# @param delay delay between two measurement, default 60000 (1 minute)
# @param output output file name (open in append mode), default dna03.txt
# @param debuglevel 0/1/2, default 0 - off
source dna03.tcl
source common.tcl

global argv argc 

set debuglevel 0
set ofname "dna03.txt"
set delay 60000

if {$argc > 0} {
	set delay [lindex $argv 0]
}
if {$argc > 1} {
	set ofname [lindex $argv 1]
}
if {$argc > 2} {
	set debugmode [lindex $argv 2]
}
OpenCom
set of [open $ofname "a"]

# turn off sleep mode
SetAutoOff 0
while {1} {
	set systemTime [clock seconds]
	set res [Measure]
	if {[llength $res] == 2} {
		puts "[GetVal 330 $res] [GetVal 11 $res] [clock format $systemTime -format %H:%M:%S]"
		puts $of "[GetVal 330 $res] [GetVal 11 $res] [clock format $systemTime -format %H:%M:%S]"
	} else {
		puts $res
		puts $of $res
	}
	flush $of
	after $delay
}
