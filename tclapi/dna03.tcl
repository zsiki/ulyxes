#//#
#	Leica DNA03 specific functions
#	<p></p>
#	<p>Ulyxes - an open source project to drive total stations and
#			publish observation results</p>
#	<p>GPL v2.0 license</p>
#	<p>Copyright (C) 2010-2012 Zoltan Siki <siki@agt.bme.hu></p>
#	@author Zoltan Siki 
#	@author Daniel Moka (TclDoc comments)
#	@version 1.0
#//#

if {![info exists debuglevel]} {
	source global.tcl
}

# load serial communication procs
source leica_com.tcl

#===============================================================================
# low level commands for instrument
#===============================================================================

# dividers for unit conversion to meters
set unit_div(0) 1000.0
set unit_div(1) [expr {1000.0 / 0.3048}]
set unit_div(6) 10000.0
set unit_div(7) [expr {10000.0 / 0.3048}]
set unit_div(8) 100000.0

# Measure horizontal distance and staff reading
#	@return list of observations: {{330 v} {11 hd}} or error code
proc Measure {} {
global buf
global unit_div
	set code 0
	# start meaurement
	if {[set res [Send "GET/M/WI32/WI330"]] != ""} { return $res}
	if {[regexp "^@\[EW\](\[0-9\]+)$" $buf code]} { return $code}
	set buflist [split [string trim $buf]]
	set obuf {}
	set d 0
	set r 0
	foreach item $buflist {
		switch -regexp $item {
			"^32\." {	;# distance
				set d [string trimleft [string range $item 7 end] 0]
				# change to meter
				set d [expr {$d / $unit_div([string index $item 5])}]
			}
			"^330" {	;# staff reading
				set r [string trimleft [string range $item 7 end] 0]
				# change to meter
				set r [expr {$r / $unit_div([string index $item 5])}]
			}
		}
	}
	lappend obuf [list 11 $d]
	lappend obuf [list 330 $r]
	return $obuf
}

# Get internal temperature
#	@param none
#	@return list of observations: {{56 temp}} or error code
proc GetTemp {} {
global buf
global unit_div
	set code 0
	# query instrument
	if {[set res [Send "GET/M/WI95"]] != ""} { return $res}
	if {[regexp "^@\[EW\](\[0-9\]+)$" $buf code]} { return $code}
	set buflist [split [string trim $buf]]
	set obuf {}
	set t 0
	foreach item $buflist {
		switch -regexp $item {
			"^95" {	;# temperature
				set t [string trimleft [string range $item 7 end] 0]
				# change unit
				set t [expr {$t / $unit_div([string index $item 5])}]
			}
		}
	}
	lappend obuf [list 56 $t]
}

# Set autooff
#	@param par 0/1/2 - Off/On/Sleep mode
#	@return 0 on success, other int value on error
proc SetAutoOff {par} {
global buf
	if {$par <0 || $par > 2} { return -1}
	if {[set res [Send "SET/95/$par"]] != ""} { return -2}
	return 0
}

# Query autooff state
#	@return 0/1/2 - Off/On/Sleep mode
proc GetAutoOff {} {
global buf
	if {[set res [Send "CONF/95"]] != ""} { return -2}
	return [string index $buf end]
}
