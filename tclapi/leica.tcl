#//#
#	Leica TCA1800/RTS1200 specific functions
#	<p></p>
#	<p>Ulyxes - an open source project to drive total stations and
#			publish observation results</p>
#	<p>GPL v2.0 license</p>
#	<p>Copyright (C) 2010-2012 Zoltan Siki <siki@agt.bme.hu></p>
#	@author Zoltan Siki 
#	@author Daniel Moka (TclDoc comments)
#	@version 1.1
#//#

if {![info exists debuglevel]} {
	source global.tcl
}

# load serial communication procs
source leica_com.tcl
#===============================================================================
# low level commands for instrument
#===============================================================================


# Set prism constant
#	@param pc prism constant to set, mm unit
#	@return 0 on succes or nonzero error code
proc SetPc {pc} {
	set pc [format %.1f $pc]	;# set tenth of milimeter
	# send value to instrument
	if {[set res [Send "%R1Q,2024:$pc"]] != 0} {
		return $res
	}
	return 0
}

# Get prism constant
#	@return pc, mm unit
proc GetPc {} {
	global buf
	if {[set res [Send "%R1Q,2023:"]] != 0} {
		return $res
	}
	# process input buffer
	set buflist [split $buf ",:"]
	return [lindex $buflist 4]
}

# Set ATR status on/off
#	@param atr 0/1 = off/on
# 	@return 0 or error code
proc SetATR {atr} {
	if {[set res [Send "%R1Q,18005:$atr"]] != 0} {
		# try old command for old instruments
		if {[set res [Send "%R1Q,9018:$atr"]] != 0} {
			return $res
		}
	}
	return 0
}

# Get ATR status
#	@return 0/1 - off/on 
proc GetATR {} {
	global buf
	if {[set res [Send "%R1Q,18006:"]] != 0} {
		# try old command for old instruments
		if {[set res [Send "%R1Q,9019:"]] != 0} {
			return $res
		}
	}
	# process input buffer
	set buflist [split $buf ",:"]
	return [lindex $buflist 4]
}

# Set Lock status on/off
#	@param lock 0/1 = off/on
#	@return 0 or error code
proc SetLock {lock} {
	if {[set res [Send "%R1Q,18007:$lock"]] != 0} {
		# try old command for old instruments
		if {[set res [Send "%R1Q,9018:$lock"]] != 0} {
			return $res
		}
	}
	return 0
}

# Get Lock status
#	@return 0/1 - off/on 
proc GetLock {} {
	global buf
	if {[set res [Send "%R1Q,18008:"]] != 0} {
		# try old command for old instruments
		if {[set res [Send "%R1Q,9021:"]] != 0} {
			return $res
		}
	}
	# process input buffer
	set buflist [split $buf ",:"]
	return [lindex $buflist 4]
}

# Get atmospheric correction settings
#	@return atmospheric settings as a list {lambda pressure drytemp wettemp}
proc GetAtmCorr {} {
	global buf
	if {[set res [Send "%R1Q,2029:"]] != 0} {
		return $res
	}
	# process input buffer
	set buflist [split $buf ",:"]
	return [lrange $buflist 4 end]
}

# Set atmospheric correction settings
#	@param lambda Constant for the instrument not changeable, use GetAtmCorr to get value
#	@param pres pressure value
#	@param dry dry temperature
#	@param wet wet temperature
#	@return 0 or error code
proc SetAtmCorr {lambda pres dry wet} {
	if {[set res [Send "%R1Q,2028:$lambda,$pres,$dry,$wet"]] != 0} {
		return $res
	}
	return 0
}

# Get refraction correction setting
#	@return refraction correction as a list {on earthradius scale}
proc GetRefCorr {} {
	global buf
	if {[set res [Send "%R1Q,2031:"]] != 0} {
		return $res
	}
	# process input buffer
	set buflist [split $buf ",:"]
	return [lrange $buflist 4 end]
}

# Set refraction correction settings
#	@param on 0/1 off/on
#	@param r earth radius
#	@param s refractice scale
#	@return 0 or error code
proc SetRefCorr {on r s} {
# TBD
	if {[set res [Send "%R1Q,2030:$on,$r,$s"]] != 0} {
		return $res
	}
	return 0
}

# Get station co-ordinates
#	@return list {{37 N} {38 E} {39 Z}}
proc GetStation {} {
	global buf
	if {[set res [Send "%R1Q,2009:"]] != 0} {
		return $res
	}
	# process input buffer
	set buflist [split $buf ",:"]
	set res {}
	lappend res [list 38 [lindex $buflist 4]]
	lappend res [list 37 [lindex $buflist 5]]
	lappend res [list 39 [lindex $buflist 6]]
	return $res
}

# Set station coordinates
#	@param e easting
#	@param n northing
#	@param z elevation
#	@return 0 or error code
proc SetStation {e n z} {
	global buf
	if {[set res [Send "%R1Q,2010:$e,$n,$z"]] != 0} {
		return $res
	}
	return 0
}

# Get EDM (Electronic Distance Meter) mode 
#	@return mode
proc GetEDMMode {} {
	global buf
	if {[set res [Send "%R1Q,2021:"]] != 0} {
		return $res
	}
	# process input buffer
	set buflist [split $buf ",:"]
	return [lindex $buflist 4]
}

# Set EDM mode
#	@param mode EDM mode to set<br />
#		0 - 
#		1 - single to tape<br />
#		2 - single to prism<br />
#		3 - single fast to prism<br />
#		4 - single long range<br />
#		5 - single short range/ reflector less<br />
#		6 - tracking to prism<br />
#		7 - tracking dynamic<br />
#		8 - tracking reflector less<br />
#		9 - tracking fast<br />
#		10- averaging to prism<br />
#		11- averaging short range<br />
#		12- averaging long range<br />
#	@return 0 on success, non zero in case of error
# TBD modes are changed
proc SetEDMMode {mode} {
	global buf
	if {[set res [Send "%R1Q,2020:$mode"]] != 0} {
		return $res
	}
	return 0
}

# Set orientation angle
#	@param ori whole circle bearing for the actual direction
#	@param unit unit for bearing, optional (default RAD)
#	@return return 0 or error code
proc SetOri {ori {units RAD}} {
	global buf
	# clear distance first
	if {[set res [Measure 3]] != 0} { return $res }
	# convert to radians
	set ori_rad [ChangeAngle $ori $units "RAD"]
	if {[set res [Send "%R1Q,2113:$ori_rad"]] != 0} {
		return $res
	}
	return 0
}

# Set RCS searching mode
proc SetRCS {rcs} {
	if {[set res [Send "%R1Q,18009:$rcs"]] != 0} {
		return $res
	}
	return 0
}

# Rotate instrument to given direction
#	@param hz horizontal direction
#	@param v zenith angle
#	@param units units for angles, optional (default RAD) see ChangeAngle
#	@param atr 0/1 no atr/with atr, optional (default 0)
#	@return return 0 or error code
proc Move {hz v {units "RAD"} {atr 0}} {
	# convert to radians
	set hz_rad [ChangeAngle $hz $units "RAD"]
	set v_rad [ChangeAngle $v $units "RAD"]
	# rotate instrument
	if {[set res [Send "%R1Q,9027:$hz_rad,$v_rad,0,$atr,0"]] != 0} {
		return $res
	}
	return 0
}

# Measure distance
#<p>[NOTE: call "Measure 3" to clear previous distance measurement]</p>
#	@param prg measure program 1/2/3/... = default/track/clear..., optional (default 1)
#	@param wait time in ms, optional (default 12000)
#	@param incl inclination calculation - 0/1/2 = measure always (slow)/calculate (fast)/automatic, optional (default 0)
#	@return list of observations: {{7 hz} {8 v} {9 sd}} or error code
proc Measure {{prg 1} {wait 12000} {incl 0}} {
global buf
	# start distance meaurement
	if {[set res [Send "%R1Q,2008:$prg,$incl"]] != 0} { return $res}
	if {$prg == 3} {
		# clear distance only and return
		return $res
	}
	if {[set res [Send "%R1Q,2108:$wait,$incl"]] != 0} { return $res}
	# process input buffer
	set buflist [split $buf ",:"]
	set res {}
	lappend res [list 7 [lindex $buflist 4]]
	lappend res [list 8 [lindex $buflist 5]]
	lappend res [list 9 [lindex $buflist 6]]
	return $res
}

# Measure distance
#	@return list of observations: {{7 hz} {8 v} {9 sd}} 
proc Measure1 {} {
global buf
	if {[set res [Send "%R1Q,17017:2"]] != 0} { return $res}
	# process input buffer
	set buflist [split $buf ",:"]
	set res {}
	lappend res [list 7 [lindex $buflist 4]]
	lappend res [list 8 [lindex $buflist 5]]
	lappend res [list 9 [lindex $buflist 6]]
	return $res
}

# Rotate the instrument and measure distance 
#	@param hz horizontal direction
#	@param v zenith angle
#	@param units angle unit, optional (default RAD)
#	@param atr 0/1 atr off/on
proc MoveAndMeasure {hz v {units "RAD"} {atr 0}} {
	if {[set res [Move $hz $v $units $atr]] != 0} { return $res }
	if {[llength [set res [Measure]]] == 1} { return $res }
	return $res
}

# Read coordinates from instrument calculated from last distance measurement
#	@param wait wait time in ms, optional (default 1000)
#	@param incl inclination calculation - 0/1/2 = measure always (slow)/calculate (fast)/automatic, optional (default 0)
#	@return coordinate list : {{38 Easting} {37 Northing} {39 Height}}
proc Coords {{wait 1000} {incl 0}} {
global buf
	# start distance measurement
	if {[set res [Send "%R1Q,2082:$wait,$incl"]] != 0} { return $res}
	set buflist [split $buf ":,"]
	set res {}
	lappend res [list 38 [lindex $buflist 4]]
	lappend res [list 37 [lindex $buflist 5]]
	lappend res [list 39 [lindex $buflist 6]]
	return $res
}

# Read angles from instrument
#	@return angles in radian in a list: {{7 hz} {8 v}}
proc GetAngles {} {
global buf
	if {[set res [Send "%R1Q,2003:0"]] != 0} { return $res}
	set buflist [split $buf ":,"]
	set res {}
       	lappend res [list 7 [lindex $buflist 4]]
	lappend res [list 8 [lindex $buflist 5]]
	return $res
}

# Read instrument name
#	@return instrument name
proc GetInstrument {} {
global buf
# TODO error result and normal output to separate?
	if {[set res [Send "%R1Q,5004:0"]] != 0} { return $res}
	set buflist [split $buf ":,"]
	return [lindex $buflist 4]
}

# Read instrument id
#	@return instrument id
proc GetId {} {
global buf
# TODO error result and normal output to separate?
	if {[set res [Send "%R1Q,5003:0"]] != 0} { return $res}
	set buflist [split $buf ":,"]
	return [lindex $buflist 4]
}

# Search prism in a given area (elliptical)
#	@param hzArea horizontal search region
#	@param vArea vertical search region
#	@param units units for hzArea and vArea
#	@return 0 on success or error code
# TODO check 17020
proc Search {hzArea vArea {units "RAD"}} {
	set hz_rad [ChangeAngle $hzArea $units "RAD"]
	set v_rad [ChangeAngle $vArea $units "RAD"]
	set res [Send "%R1Q,9029:$hz_rad,$v_rad,0"]
	return $res
}

# Get internal temperature
#	@return internal temperature in Celsius
proc GetIntTemp {} {
	global buf
	set res [Send "%R1Q,5011:"]
	# process input buffer
	set buflist [split $buf ",:"]
	return [lindex $buflist 3]
}


