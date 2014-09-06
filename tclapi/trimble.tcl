#//#
# 	Trimble 550x specific functions
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

#===============================================================================
# Low level communication functions for com port
#===============================================================================


# Read input from com port.
# <p>Input chars are added to global input buffer (buf)</p>
proc ReadCom {} {
global buf	;# input buffer
global com
global debuglevel

	if {[catch {set cmsg [read $com 1]} msg]} {
		# in case of error write error message
		puts $msg
		CloseCom
	}
	if {[string length $cmsg]} {
		if {$debuglevel > 1} {
			puts "in=$cmsg"	;# echo input char
		}
		set buf "$buf$cmsg"	;# append char to input buffer
	}
	if {[eof $com]} {
		puts "EOF"
		CloseCom
		return
	}
}

# Close communication port
proc CloseCom {} {
global com
	if {[catch {close $com} msg] == 1} {
		puts "error closing $com $msg"
	}
}

# Open communication port, port number and other parameters are read from a file
# <br>(sets global variable com)
#	@param par name of parameter file, optional (default trimble5503.com)
#	@return 0 on success on nonzero error code
proc OpenCom {{par "trimble5503.com"}} {
global com

	if {[catch {source $par} msg] == 1} {
		puts "error openinng $par $msg"
		return 1
	}
	if {[catch {set com [open $actPars(port) RDWR]} msg] == 1} {
		puts "error opening $com $msg"
		return 1
	}
	if {[catch {fconfigure $com \
	-mode $actPars(baud),$actPars(parity),$actPars(data),$actPars(stop) \
		-blocking $actPars(blocking) \
		-translation $actPars(translation) \
		-buffering $actPars(buffering) \
		-buffersize $actPars(buffsize)} msg] == 1} {
		close $com
		puts "error configuring $com $msg"
		return 1
	}
	return 0
}

# Send message to the instrument and wait for answer
#	@param msg message to send
#	@return 0 on success or nonzero error status
proc Send {msg} {
global buf
global com
global debuglevel
global max

	# clear buf previous data LOST !!!!
	set buf ""
	if {$debuglevel} {
		puts "$msg -- sent"
	}
	if {[catch {puts $com $msg} err] == 1} {
		puts "error writing $com: $err"
		return -1
	}
	after 1000
	set c ""
	set i 0
	while {[string index $c 0] != ">" && $i < $max} {
		if {[catch {set c [read $com 1]} err] == 1} {
			puts "error reading $com: $err"
			return -2
		}
		if {[string length $c]} {
			set buf "$buf$c"
			if {$debuglevel > 1} {
				puts "read: $c"
			}
		}
		incr i
		after 100
	}
	if {$i >= $max} {
		if {$debuglevel} {
			puts "error: timeout"
		}
		return -3
	}
	set res [lindex [split $buf "\n"] 0]
	if {$res == ">"} { return 0 }
	if {[regexp $res "^\[0-9\]+$"]} { return $res }
	return 0
}

#===============================================================================
# low level commands for instrument
#===============================================================================


# Set prism constant
#	@param pc prism constant in mm
# 	@return 0 on success or nonzero error code
proc SetPc {pc} {
	set pc [format "%.3f" [expr {$pc / 1000.0}]]	;# change to meters
	# send value to instrument
	if {[set res [Send "WG,20=$pc"]] != 0} {
		return $res
	}
	return 0
}

# Get prism constant
# 	@return pc in mm
proc GetPc {} {
	global buf
	if {[set res [Send "RG,20"]] != 0} {
		return $res
	}
	# process input buffer
	set buflist [split $buf "="]
	return [lindex $buflist 1]
}

# Set ATR status -- dummy function for compatibility purposes
#	@param atr 0/1 = off/on
# 	@return -1 (always error)
proc SetATR {atr} {
	return -1
}

# Get ATR status -- dummy function for compatibility purposes
# 	@return -1 (always error)
proc GetATR {} {
	return -1
}

# Set Lock status -- dummy function for compatibility purposes
# 	@param lock - 0/1 = off/on
#	@return -1 (always error)
proc SetLock {lock} {
	return -1
}

# Get Lock status
# 	@return -1 (always error)
proc GetLock {} {
	return -1
}

# Get atmospheric correction settings
# 	@return atmospheric settings as a list {ppm pressure drytemp wettemp}
proc GetAtmCorr {} {
	global buf
	# get correction ppm
	if {[set res [Send "RG,30"]] != 0} {
		return $res
	}
	set ppm [lindex [split $buf "=\n"] 1]
	# get air pressure
	if {[set res [Send "RG,74"]] != 0} {
		return $res
	}
	set pres [lindex [split $buf "=\n"] 1]
	# get temperature
	if {[set res [Send "RG,56"]] != 0} {
		return $res
	}
	set drytemp [lindex [split $buf "=\n"] 1]
	# get wet temperature
	if {[set res [Send "RG,66"]] != 0} {
		return $res
	}
	set wettemp [lindex [split $buf "=\n"] 1]

	return [list $ppm $pres $drytemp $wettemp]
}

# Set atmospheric correction setting
#	@param ppm correction
#   @parampres pressure value
#	@paramd dry dry temperature
#	@param wet wet temperature
# 	@return 0 or error code
proc SetAtmCorr {ppm pres dry wet} {
	if {[set res [Send "WG,30=$ppm"]] != 0} {
		return $res
	}
	if {[set res [Send "WG,74=$pres"]] != 0} {
		return $res
	}
	if {[set res [Send "WG,56=$dry"]] != 0} {
		return $res
	}
	return 0
}

# Get refraction correction settings
# 	@return refraction settings as a list {on earthradius scale}
proc GetRefCorr {} {
	global buf
	# scale ?? TBD
	if {[set res [Send "RG,59"]] != 0} {
		return $res
	}
	set scale [lindex [split $buf "=\n"] 1]
	# earth radius
	if {[set res [Send "RG,58"]] != 0} {
		return $res
	}
	set radius [lindex [split $buf "=\n"] 1]
	return [list 1 $radius $scale]
}

# Set refraction correction on/off
#	@param on 0/1 off/on
#   @param r earth radius
#	@param s refractive scale
# 	@return 0 or error code
proc SetRefCorr {on r s} {
	# scale
	if {[set res [Send "WG,59=$s"]] != 0} {
		return $res
	}
	# earth radius
	if {[set res [Send "WG,58=$r"]] != 0} {
		return $res
	}
	return 0
}

# Get station co-ordinates (dummy proc for compatibility puspose)
# 	@return -1 (always error)
proc GetStation {} {
	return -1
}

# Set station coordinates (dummy proc for compatibility puspose)
#	@param e easting
#	@param n northing
#	@param z elevation
# 	@return -1 (always error)
proc SetStation {e n z} {
	return -1
}

# Get EDM (Electronic Distance Meter) mode 
#	@return mode
proc GetEDMMode {} {
# TBD
	return -1
}

# Set EDM mode
#	@param mode EDM mode to set
#		1 - single to tape
#		2 - single to prism
#		3 - single fast to prism
#		4 - single long range
#		5 - single short range
#		6 - tracking to prism
#		7 - tracking dynamic
#		8 - tracking reflector less
#		9 - tracking fast
#		10- averaging to prism
#		11- averaging short range
#		12- averaging long range
#	@return 0 on success, non zero in case of error
proc SetEDMMode {mode} {
# TBD
	return -1
}

# Set orientation angle
#	@param ori orientation angle 
# 	@return 0 or error code
proc SetOri {ori {units DEG}} {
	global buf
	# convert pseudo DMS
	set ori_d [ChangeAngle $ori $units "DEG"]
	if {[set res [Send "WG,21=$ori_d"]] != 0} {
		return $res
	}
	return 0
}

# Rotate instrument to given direction
#	@param hz horizontal direction, pseudo dms (ddd.mmss)
#	@param v zenith angle, pseudo dms (ddd.mmss)
#	@param units DEG/RAD/DMS
#	@param atr not used, only for compability purposes
# 	@return 0 or error code
proc Move {hz v {units "RAD"} {atr 0}} {
	# convert pseudo DMS
	set hz_d [ChangeAngle $hz $units "DEG"]
	set v_d [ChangeAngle $v $units "DEG"]
	set hz_d [format %.4f $hz_d]	;# set number of decimals
	set v_d [format %.4f $v_d]	;# set number of decimals
	# set vertical angle
	if {[set res [Send "WG,26=$v"]] != 0} { return $res }
	# set horizontal angle
	if {[set res [Send "WG,27=$hz"]] != 0} { return $res }
	# rotate instrument
	if {[set res [Send "WS=PH02V02"]] != 0} { return $res}
	return 0
}

# Measure distance
#	@param prg measure program 1/2/.. standard/track TBD
#	@param wait not used (only for compability purposes)
#	@param incl not used (only for compability purposes)
# 	@return error code or list of observations: {{7 hz} {8 v} {9 sd}}	
proc Measure {{prg 1} {wait 2000} {incl 0}} {
global buf
	# start distance measurement
	if {[set res [Send "TG"]] != 0} { return $res}
	after 2000
	# read observation data
	set ans ""
	if {[set res [Send "RG"]] != 0} { return $res}
	set ans [split $buf "\n"]
	set l {}
	foreach item [lrange $ans 1 end] {
		set w [split $item "="]
		if {[llength $w] == 2} {
			lappend l $w ;# GeoEasy likes list
		}
	}
	return $l
}

# Rotate the instrument and measure distance
#	@param hz horizontal direction
#	@param v zenith angle
#	@param atr not used only for compability purposes
#	@return 0 in case of error
proc MoveAndMeasure {hz v {units "RAD"} {atr 0}} {
	if {[set res [Move $hz $v $units]] != 0} { return $res }
	after 1000
	if {[set res [Measure]] != 0} { return $res }
	return 0
}

# Read coordinates from instrument
#	@param wait (not used only for compatibility)
#	@param incl (not used only for compatibility)
# 	@return coordinates from instrument : {{38 Easting} {37 Northing} {39 Height}}
proc Coords {{wait 100} {incl 0}} {
global buf
	set l {}
	if {[set res [Send "RG,37"]] != 0} { return $res }
	lappend l [lrange [split $buf "=\n"] 0 1]
	if {[set res [Send "RG,38"]] != 0} { return $res }
	lappend l [lrange [split $buf "=\n"] 0 1]
	if {[set res [Send "RG,39"]] != 0} { return $res }
	lappend l [lrange [split $buf "=\n"] 0 1]
	return $l
}

# Read angles from instrument
#	@return angles in radians in a list : {{7 hz} {8 v}}
proc GetAngles {} {
global buf
	set l {}
	if {[set res [Send "RG,7"]] != 0} { return $res }
	lappend l [list 7 [Deg2Rad [lindex [split $buf "=\n"] 1]]]
	if {[set res [Send "RG,8"]] != 0} { return $res }
	lappend l [list 8 [Deg2Rad [lindex [split $buf "=\n"] 1]]]
	return $l
}

# Read instrument name
#	@return instrument name
proc GetInstrument {} {
global buf
	return "Trimble 550x"
}

# Read instrument id
#	@return instrument id or error code
proc GetId {} {
global buf
	if {[set res [Send "RG,55"]] != 0} {return $res}
	return [lindex [split $buf "=\n"] 1]
}

