# nmea test
source global.tcl
source common.tcl
source nmea.tcl
source nmea_com.tcl

set debuglevel 1
OpenCom
while {1} {
	puts [Coords]
}
CloseCom
