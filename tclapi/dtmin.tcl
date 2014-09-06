#//#
#	Load ESRI ASCII GRID
#	<p></p>
#	<p>Ulyxes - an open source project to drive total stations and
#			publish observation results</p>
#	<p>GPL v2.0 license</p>
#	<p>Copyright (C) 2010-2012 Zoltan Siki <siki@agt.bme.hu></p>
#	@author Zoltan Siki 
#	@version 1.1
#//#

# Load an ESRI ASCII GRID from file, elevation array is returned in a global variable dtm
#	@param dtmname name of ESRI ASCII GRID file
#	@return list of number_of columns number_of_rows east_ll_corner north_ll_corner
proc DtmIn {dtmname} {
	global dtm
	set fp [open $dtmname]
	# load grid header
	for {set i 0} {$i < 6} {incr i} {
		set buf [gets $fp]
		set buflist [split $buf]
		switch -exact [lindex $buflist 0] {
			"ncols" {
				set ncols [lindex $buflist 1]
			}
			"nrows" {
				set nrows [lindex $buflist 1]
			}
			"xllcorner" {
				set xllcorner [lindex $buflist 1]
			}
			"yllcorner" {
				set yllcorner [lindex $buflist 1]
			}
			"cellsize" {
				set cellsize [lindex $buflist 1]
			}
			"nodata_value" {
				set nodata_value [lindex $buflist 1]
			}
		}
	}
	# load elevations
	for {set row 0} {$row < $nrows} {incr row} {
		set buf [gets $fp]
		set buflist [split $buf]
		for {set col 0} {$col < $ncols} {incr col} {
			set dtm($row,$col) [lindex $buflist $col]
		}
	}
	return [list $ncols $nrows $xllcorner $yllcorner $cellsize $nodata_value]
}
