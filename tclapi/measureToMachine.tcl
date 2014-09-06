# !/bin/sh
# the next line restarts using tclsh \
exec tclsh "$0" "$@"	

#//#
#	This program measures to a moving object (car) and checks the object
#	is moving on a predefined path. Report is sent to standard ouput
#
#	@param tolerance maximal distance from the path which is accepted
#	@param coordinates input file with the coordinates of the path to
#	@param com name of RS-232 parameter file, optional (default leica.com)
#	follow. It is a .coo file, points must have horizontal coordinates.
#	
#	<p><b>Changes<br />
#	2013.04.16. setting log & atr Siki
#	</p>
#	<p>Ulyses - an open source project to drive total stations and
#			publish observation results</p>
#	<p>GPL v2.0 license</p>
#	<p>Copyright (C) 2010-2012 Zoltan Siki <siki@agt.bme.hu></p>
#	@author Daniel Moka
#	@version 1.2
#//#

source global.tcl
source common.tcl
source leica.tcl

global argv argc
global coo

set tol 5
set debuglevel 2
if {$argc < 2} {
	puts "usage: measureToMachine tolerance coo_file <com_file> <debuglevel>"
	exit 1
}
set limit [lindex $argv 0]
set cooFile [lindex $argv 1]
set com "leica.com"
if {$argc > 2} {set com [lindex $argv 2]}
set debuglevel 0
if {$argc > 3} {set debuglevel [lindex $argv 3]}

# Open and set communication port
if {[OpenCom $com]} {
	# error opening RS-232 parameter file
	puts "Error on RS-232"
	exit 1
}
if {[LoadCoo $cooFile]} {
	puts "Error on coo file"
	exit 2
}
SetLock 0
SetATR 1
Measure
SetLock 1
Measure
Measure
Measure
SetEDMMode 6	;# tracking
set pn 1
while {1} {
	set systemTime [clock seconds]  ;# set current time
	set res [Coords]
	if {[llength $res] > 1} {
lappend $res [list 5 $pn]
puts stdout $res
		set y [GetVal 38 $res]
		set x [GetVal 37 $res]
		puts stdout "x: $x y: $y"
		set mind 1e38
		set yj [GetVal 38 $coo(1)]
		set xj [GetVal 37 $coo(1)]
		for {set j 2} {$j <= [array size coo]} {incr j} {
			set yi $yj
			set xi $xj
			set yj [GetVal 38 $coo($j)]
			set xj [GetVal 37 $coo($j)]
			set miny [expr {$yi < $yj ? $yi - $tol : $yj - $tol}]
			set minx [expr {$xi < $xj ? $xi - $tol : $xj - $tol}]
			set maxy [expr {$yi > $yj ? $yi + $tol : $yj + $tol}]
			set maxx [expr {$xi > $xj ? $xi + $tol : $xj + $tol}]
			if {$minx < $x && $x < $maxx && $miny < $y && $y < $maxy } {
				# calculate the equation of a line
				set l [Line2D $xi $yi $xj $yj]
				# calculates distance between measured point and the line
				set d [LinePointDist [lindex $l 0] [lindex $l 1] [lindex $l 2] $x $y ]
				puts stdout "dist: $d  i: [expr {$j-1}]  j:$j"
				if {$d < $mind} {
					set mind $d
				}
			}
		}
		if {$mind > $limit} {
			puts stdout "*** y: $y x: $x dist: $mind at [clock format $systemTime -format %H:%M:%S]"
			Beep 5
		} else {
			if {$debuglevel > 0} {
				puts stdout "OK  y: $y x: $x dist: $mind at [clock format $systemTime -format %H:%M:%S]"
			}
		}
	} else {
		puts stdout "ERROR $res"
	}
}
