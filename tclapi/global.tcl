#//#
# global.tcl - this file sets up the following useful global constants:
#	<ul>
#	<li>debuglevel: 0/1/2 no warnings/serious warnings/all debug messages</li>
#	<li>PI: relationship between the diameter and the perimeter of a circle</li>
#	<li>PI2: 2 times PI</li>
#	<li>RO: 180*3600/PI, 1 radian in seconds</li>
#	<li>max: maximum number of tries to get answer from the instrument used in Send</li>
#	<li>maxtry: maximum number of tries to find prism used in Robot</li>
#	<li>com: used port name e.g. com1: or /dev/tty/</li>
#	<li>buf: I/O buffer for serial port</li>
#	<li>reg: array with 4 regexp</li>
#		<ul>
#		<li>reg(0): for any text</li>
#		<li>reg(1): for integer value</li>
#		<li>reg(2): for float values</li>
#		<li>reg(3): fom DMS values</li>
#		</ul>
#	</ul>
#	<p></p>
#	<p>Ulyxes - an open source project to drive total stations and</p>
#			publish observation results</p>
#	<p>GPL v2.0 license</p>
#	<p>Copyright (C) 2010-2012 Zoltan Siki <siki@agt.bme.hu></p>
#	@author Zoltan Siki 
#	@author Daniel Moka (TclDoc comments)
#	@version 1.1
#//#

# Useful global constants/parameters
set debuglevel 2	;# debuglevel 0/1/2 no warnings/serious warnings/all debug messages
set PI [expr {4.0 * atan(1)}]
set PI2 [expr {2.0 * $PI}]
set RO [expr {180.0 * 60.0 * 60.0 / $PI}]
set max 1000	;# maximum number of tries to get answer from the instrument used in Send
set maxtry 3	;# maximum number of tries to find prism used in Robot

# initialise global variables
set com ""	;# used port name e.g. com1: or /dev/tty/
set buf ""	;# I/O buffer for port
# regexps
set reg(0) ".*"	;# any text
set reg(1) "^-?\[0-9\]+$"	;# integer
set reg(2) "^-?\[0-9\]+(\\.\[0-9\]*)?(\[eE\]\[+-\]?\[0-9\]*)?$"	;# float
set reg(3) "^\[0-9\]\[0-9\]?\[0-9\]?(-\[0-9\]\[0-9\]?)?(-\[0-9\]\[0-9\]?(\.\[0-9\]*)?)?$"	;# DMS
