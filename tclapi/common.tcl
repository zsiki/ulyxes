#//#
# common.tcl - this file contains common instrument independent functions
#	<p>Ulyxes - an open source project to drive total stations and
#			publish observation results</p>
#	<p>GPL v2.0 license</p>
#	<p>Copyright (C) 2010-2012 Zoltan Siki <siki@agt.bme.hu></p>
#	@author Zoltan Siki 
#	@author Daniel Moka (TclDoc comments)
#	@version 1.0
#//#

# Conversion function:
#
# Convert sexagesimal angle to radian
#	@param angle in pseudo dms format (ddd.mmss)
# 	@return angle in radians
proc Deg2Rad {deg} {
	global PI
	set d [expr {int(floor($deg))}]
	set m [expr {int(floor(($deg - $d) * 100))}]
	set s [expr {($deg - $d - $m / 100.0) * 10000.0}]
	return [expr {($d + $m / 60.0 + $s / 3600.0) / 180.0 * $PI}]
}

# Conversion function:
#
# Convert radian to sexagesimal into pseudo dms (ddd.mmss) format
#	@param angle value in radian
#	@return angle in pseudo DMS
proc Rad2Deg {angle} {
	global PI
	set d [expr {$angle * 180.0 / $PI}]	;# decimal degrees
	set dd [expr {int(floor($d))}]
	set m [expr {($d -$dd) * 60.0}]
	set mm [expr {int(floor($m))}]
	set ss [expr {int(($m -$mm) * 60.0)}]
	return "$dd.$mm$ss"
}

# Conversion function: 
#
# Convert angle from gon to radian
#	@param angle value in gon
#	@return angle in radian
proc Gon2Rad {angle} {
	global PI
	return [expr {$angle / 200.0 * $PI}]
}

# Conversion function:
#
# Convert angle from radian to gon
#	@param angle angle value in radian
#	@return angle in gon
proc Rad2Gon {angle} {
	global PI
	return [expr {$angle / $PI * 200.0}]
}

# Conversion function:
#
#	Convert angle from radian to seconds (ss)
#	@param angle angle value in radian
#	@return angle in second
proc Rad2Sec {rad} {
	global RO
	return [expr {$rad * $RO}]
}

# Conversion function:
#
# Convert angle from DMS (sexagesimal) to radian
#	@param angle in DMS (deg-min-sec) to convert into radian
#	@return angle in radian or empty string if invalid value got
proc DMS2Rad {dms} {
	global PI

	set m 0
	set s 0
	regsub -- "^(\[0-9\]+).*" $dms "\\1" d			;# degree
#	remove leading zeros
	regsub -- "^0+(.*)" $d "\\1" d
	if {$d == ""} {set d 0}
	if {[regexp "^\[0-9\]+-\[0-9\]+" $dms]} {
		regsub -- "^\[0-9\]+-(\[0-9\]+).*" $dms "\\1" m	;# minute
	}
#	remove leading zeros
	regsub -- "^0+(.*)" $m "\\1" m
	if {$m == ""} {set m 0}
	if {[regexp "^\[0-9\]+-\[0-9\]+-\[0-9\]+" $dms]} {
		regsub -- "^\[0-9\]+-\[0-9\]+-(\[0-9\]+.*)" $dms "\\1" s	;# second
	}
#	remove leading zeros
	regsub -- "^0+(.*)" $s "\\1" s
	if {$s == ""} {set s 0}
	# check limits for degree, minute & second
	if {$d > 359 || $m > 60 || $s > 60} {
		return ""
	} else {
		return [expr {($d + $m / 60.0 + $s / 3600.0) / 180.0 * $PI}]
	}
}

# Conversion function:
#
# Convert angle from DM (NMEA format) to radian
#	@param angle in DM (degmin.nnnn) to convert into radian
#	@return angle in radian
proc DM2Rad {dm} {
	global PI

	set sign 1
	set w [expr {$dm / 100.0}]
	if {$w < 0} {
		set sign -1
		set w [expr {abs($w)}]
	}
	set d [expr {floor($w)}]
	return [expr {$sign * ($d + ($w - $d) * 100. / 60.0) / 180.0 * $PI}]
}

# Conversion function:
#
# Convert radian to DMS (sexagesimal)
#	@param val angle in radian
#	@return angle in ddd-mm-ss format
proc DMS {val} {
	global PI

	set seconds [expr {$val * 180.0 / $PI * 3600}]
	set ss [expr {int($seconds)}]
	set d [expr {$ss / 3600}]
	set m [expr {($ss % 3600) / 60}]
	set s [expr {$ss % 60 + $seconds - $ss}]
	set wstr [format "%3d-%02d-%02d" $d $m [expr {round($s)}]]
	return $wstr
}

# Conversion function:
#
# Universal angle conversion function
#	@param angle the angle to convert
#	@param in actual unit of angle (DMS/DEG/RAD/GON)
#	@param out target unit for result (DMS/DEG/RAD/GON)
#	@return angle in out unit
proc ChangeAngle {angle {in "DMS"} {out "RAD"}} {
	# convert angle to radians
	switch -exact $in {
		"RAD" { set r $angle }
		"DMS" { set r [DMS2Rad $angle] }
		"DEG" { set r [Deg2Rad $angle] }
		"GON" { set r [Gon2Rad $angle] }
	}
	switch -exact $out {
		"RAD" { set o $r }
		"DMS" { set o [DMS $r] }
		"DEG" { set o [Rad2Gon $r] }
		"GON" { set o [Rad2Gon $r] }
	}
	return $o
}

# List handling function:
#
# Get value from list of lists like {{code1 value1} {code2 value2} ...}
#	@param codes list of codes to look for in buf
#	@param buf list of pair of elements like {{code1 value1} {code2 value2} ...}
#	@return value which belongs to the first code from codes found in buf or empty string if none of the codes found.
proc GetVal {codes buf} {
	foreach code $codes {
		set pos [lsearch -glob $buf "$code *"]
		if {$pos != -1} {
			return [lindex [lindex $buf $pos] 1]
		}
	}
	return ""
}
# List handling function:
#
# Delete sublist from list
#	@param codes list of codes to remove from buf
#	@param buf list of pair of elements like {{code1 value1} {code2 value2} ...}
#	@return the list without codes
proc DelVal {codes buf} {
	foreach code $codes {
		set pos [lsearch -glob $buf "$code *"]
		if {$pos != -1} {
			set buf [lreplace $buf $pos $pos]
		}
	}
	return $buf
}

# Instrument handling (instrument type independent functions):
# Rotate instrument relative to the actual position
#	@param hz_rel relative horizontal movement, + to right, - to left
#	@param v_rel relative vertical movement, + to down, - to up
#	@param units input angle unit (RAD/DMS/DEG/GON), optional
#	@param atr 0/1 move without ATR/move with ATR, optional
#	@return return 0 or error code
proc MoveRel {hz_rel v_rel {units "RAD"} {atr 0}} {
	global PI2
	# get the actual direction
	set angles [GetAngles]
	# did we get the angles?
	if {[GetVal 7 $angles] == ""} { return $angles }
	# calculate relativ to absolute
	set hz [expr {[GetVal 7 $angles] + [ChangeAngle $hz_rel $units "RAD"]}]
	while {$hz >= $PI2} { set hz [expr {$hz - $PI2}] }
	while {$hz < 0} { set hz [expr {$hz + $PI2}] }
	set v [expr {[GetVal 8 $angles] + [ChangeAngle $v_rel $units "RAD"]}]
	while {$v >= $PI2} { set v [expr {$v - $PI2}] }
	while {$v < 0} { set v [expr {$v + $PI2}] }
	return [Move $hz $v RAD $atr]
}

# Instrument handling (instrument type independent functions):
# Get Face info from instrument
#	@return faceinfo 0/1/2 error/first face/second face
proc GetFace {} {
	global PI
	set ang [GetAngles]
	set z [GetVal 8 $ang]
	if {$z == ""} { return 0 }
	if {$z < $PI} { return 1 }
	return 2
}

# Instrument handling (instrument type independent functions):
# Display angles on standard output
#	@param anglist code list with angle values in radian {{7 hz} {8 v} ...}
#	@param unit for output
proc DisplayAngles {anglist {unit "DMS"}} {
	puts "[ChangeAngle [GetVal 7 $anglist] "RAD" $unit] [ChangeAngle [GetVal 8 $anglist] "RAD" $unit]"
}

# Load GeoEasy coordinate file into global array coo<br />
# WARNING previous content of coo array lost!
#	<p>Returned error codes:</p>
#	<ul>
#	<li>-1: cannot open file</li>
#	<li>positive value: line number with error</li>
#	</ul>
#	@param fn input file name
#	@return 0 on success or nonzero error code
proc LoadCoo {fn} {
	global coo
	global reg

	catch {unset coo}
	if {[catch {set f2 [open $fn r]}] != 0} {
		return -1
	}
#
#	Load coordinates (skip line if not 5, 2 or 62 code)
#
	set lineno 0
	while {! [eof $f2]} {
		gets $f2 buf
		if {[string length [string trim $buf]] == 0} {continue}
		if {[catch {set pn [GetVal 5 $buf]} msg]} {
			catch {close $f2}
			return [expr {$lineno + 1}]	
		}

		if {$pn == ""} {
			catch {close $f2}
			return [expr {$lineno + 1}]	
		}
		foreach code {37 38 39} {
			if {[set w [GetVal $code $buf]] != ""} {
				if {[regexp $reg(2) $w] == 0} {
					catch {close $f2}
					return [expr {$lineno + 1}]	
				}
			}
		}
		set coo($pn) $buf
		incr lineno
	}
	catch {close $f2}
	return 0
}

# Load GeoEasy fieldbook (.geo file) into memory array geo<br />
# WARNING previous content of geo array lost!
#	<p>Returned error codes:</p>
#	<ul>
#	<li>-1: cannot open file</li>
#	<li>positive value: line number with error</li>
#	</ul>
#	@param fn file name of GeoEasy data set
#	@return 0 on success or nonzero error code
proc LoadGeo {fn} {
	global reg
	global geo

	catch {unset geo}
	if {[catch {set f1 [open $fn r]}] != 0} {
		return -1
	}
#	load station and observation records
	set lineno 0
	while {! [eof $f1]} {
		gets $f1 buf
		if {[string length [string trim $buf]] == 0} {continue}
		if {[catch {set pn [GetVal {5 2 62} $buf]} msg]} {
			catch {close $f1}
			return [expr {$lineno + 1}]	
		}
		if {$pn == ""} {
			catch {close $f1}
			return [expr {$lineno + 1}]	
		}
#	check for DMS angles (DDD-MM-SS format)
		foreach code {7 8 17 18 21 100 101 102 103} {
			if {[set w [GetVal $code $buf]] != "" && \
				[regexp $reg(3) $w]} {
				set buf [DelVal $code $buf]
				set tmp [DMS2Rad $w]
				if {[string length $w] > 0} {
					lappend buf [list $code $tmp]
				} else { 	;# invalid angle value
					catch {close $f1}
					return [expr {$lineno + 1}]	
				}
			}
		}
#	check for numeric values
		foreach code {3 6 7 8 9 10 11 17 18 21 100 101 102 103 112} {
			if {[set w [GetVal $code $buf]] != ""} {
				if {[regexp $reg(2) $w] == 0} {
					catch {close $f1}
					catch {close $f2}
					catch {close $f3}
					return [expr {$lineno + 1}]	
				}
			}
		}
		set geo($lineno) $buf
		incr lineno
	}
	catch {close $f1}
}

# Bearing function:
# Calculate whole circle bearing counter clockwise from north
#	@param ea,na coordinates of station
#	@param eb,nb coordinates of reference point
#	@return bearing in radian	
proc Bearing {ea na eb nb} {
	global PI2
	set de [expr {$eb - $ea}]
	set dn [expr {$nb - $na}]
	set w [expr {atan2($de, $dn)}]
	while {$w < 0} { set w [expr {$w + $PI2}]}
	while {$w >= $PI2} { set w [expr {$w - $PI2}]}
	return $w
}

# Distance function:
# Calculate 2D distance between two points
#	@param ea,na coordinates of station
#	@param eb,nb coordinates of reference point
#	@return bearing in radian	
proc Distance {ea na eb nb} {
	return [expr {hypot([expr {$eb - $ea}], [expr {$nb - $na}])}]
}

# Line2D calculates the equation of a line going through two points
# a * e + b * n + c = 0
#	@param e1,n1 easting and northing coordinates of startpoint
#	@param e2,n2 easting and northing coordiates of endpoint
#	@return list of line coefficients {a b c}
proc Line2D {e1 n1 e2 n2} {
	set a [expr {$n2 - $n1}]
	set b [expr {$e1 - $e2}]
	set c [expr {$e2 * $n1 - $n2 * $e1}]
	return [list $a $b $c]
}

# LinePointDist calculates distance between a point and a line
#	@param a,b,c coefficients of the equation of the line
#	@param e,n easting and northing coordinates of point
#	@return distance
proc LinePointDist {a b c e n} {
	set dw [expr {sqrt($a * $a + $b * $b)}]
	if {$dw > 0.01} {
		set d [expr {abs($a * $e + $b * $n + $c) / $dw}]
	} else {
		set d 0
	}
	return $d
}

# Beep the pc speaker
#	@param repeat number of short beeps
proc Beep {repeat} {
	for {set k 0} {$k < $repeat} {incr k} {
		puts [format "%c" 7]
	}
}
