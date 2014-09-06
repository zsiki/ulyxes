#!/bin/sh
# the next line restarts using tclsh \
exec tclsh "$0" "$@"
#//#
#	This program scans equal angle points.
#	@param scan_pars input file with scan parameters
#	Ulyses - an open source project to drive total stations and
#			publish observation results
#	GPL v2.0 license
#	Copyright (C) 2010-2012 Zoltan Siki <siki@agt.bme.hu>
#******************************************************************************
# Sample tcl script to scan
#******************************************************************************

source global.tcl
source common.tcl

global env argv argc

if {$argc == 0} {
	puts "usage: scan scan_pars"
	exit 1
}
if {[catch {source [lindex $argv 0]}]} {
	puts "Error in scan_pars"
	exit 1
}

# open and set communication port
if {[info exists compar]} {
	if {[OpenCom $compar]} {
		puts "Error opening communication port"
		exit 1
	}
} else {
	if {[OpenCom]} {
		puts "Error opening communication port"
		exit 1
	}
}
SetEDMMode 3	;# standard RL mode 
# start measurement program
set i 1
for {set hz $hz_min} {$hz <= $hz_max} {set hz [expr {$hz + $step}]} {
	for {set v $v_min} {$v <= $v_max} {set v [expr {$v + $step}]} {
		if {[set res [Move $hz $v "DEG" 0]] == 0} {
			if {[llength [set res [Measure]]] > 1} {
				if {[llength [set res [Coords]]] > 1} {
					lappend res [list 5 $i]
					puts $res
				}
			}
		}
		incr i
	}
}				
CloseCom
