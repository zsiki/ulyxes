#//#
#	Leica serial communication procs
#	<p></p>
#	<p>Ulyxes - an open source project to drive total stations and
#			publish observation results</p>
#	<p>GPL v2.0 license</p>
#	<p>Copyright (C) 2010-2012 Zoltan Siki <siki@agt.bme.hu></p>
#	@author Zoltan Siki 
#	@author Daniel Moka (TclDoc comments)
#	@version 1.1
#//#

#===============================================================================
# Low level communication functions for com port
#===============================================================================

# Read input from com port
# <p>Input chars are added to global input buffer (buf)</p>
proc ReadCom {} {
global buf	;# input buffer
global com	;# com port
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
		# port closed?
		puts "EOF"
		CloseCom
		return
	}
}

# Close communicaton port
proc CloseCom {} {
global com
global debuglevel
	if {[catch {close $com} msg] == 1} {
		if {$debuglevel > 0} {
			puts "error closing $com $msg"
		}
	}
}

# Open com port, port number and other parameters are read from a file.
# <p>Set global variable com</p>
#	@param par name of parameter file, optional (default leica.com)
#	@return 0 on success nonzero in case of error
proc OpenCom {{par "leica.com"}} {
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
		catch {close $com}
		puts "error configuring com port $msg"
		return 1
	}
	return 0
}


# Send message to the instrument and wait for answer
#	@param msg message to send
#	@return return 0 on sucess or nonzero error status
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
	while {[string length $buf] == 0 && $i < $max} {
		if {[catch {gets $com c} err] == 1} {
			puts "error reading com: $err"
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
	# check special messages of 110x %N1/%T1
	if {[string range $buf 0 2] == "%N1"} {
		if {$debuglevel > 0} {
			set ans [split [lindex [split $buf "%"] 2] ",:"]
			if {[llength $ans] == 4} {
				puts "Instrument on message"
				Send $msg
			} elseif {[lindex $ans 4] == 1} {
				puts "Instrument going to sleep"
				Send $msg
			} else {
				puts "Instrument shutting down"
				Send $msg
			}
		}
	}
	set buflist [split $buf ",:"]
	return [lindex $buflist 3]
}
