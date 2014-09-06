#//#
#	MNEA GPS handler
#	<p></p>
#	<p>Ulyxes - an open source project to drive total stations and
#			publish observation results</p>
#	<p>GPL v2.0 license</p>
#	<p>Copyright (C) 2010-2012 Zoltan Siki <siki@agt.bme.hu></p>
#	@author Zoltan Siki 
#	@author Daniel Moka (TclDoc comments)
#	@author Tamás Király
#	@version 1.1
#//#

proc Coords {{timeout 5}} {
	set start [clock seconds]
	while {[expr {[clock seconds] - $start}] < $timeout} {
		set rec [GetLine]
		if {[regexp "^.GPGGA," $rec]} {
			set reclist [split $rec ",*"]
			set quality [lindex $reclist 6]
			if {[string first $quality "12345"] != -1} {
				set lat [DM2Rad [string trimleft [lindex $reclist 2] "0"]]
				set lon [DM2Rad [string trimleft [lindex $reclist 4] "0"]]
				set height [lindex $reclist 9]
				return [list [list 37 $lat] [list 38 $lon] [list 39 $height]]
			}
		}
	}
}

proc GDOP {{timeout 5}} {
	set start [clock seconds]
	while {[expr {[clock seconds] - $start}] < $timeout} {
		set rec [GetLine]
		if {[regexp "^.GPLLK," $rec]} {
			set reclist [split $rec ",*"]
			set quality [lindex $reclist 6]
			if {[string first $quality "12345"] != -1} {
				set GDOP [lindex $reclist 9]
				return [list [list 100 $GDOP]]
			}
		}
	}
}
