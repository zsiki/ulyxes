proc ProcessList {l} {

	foreach item $l {
		if {[llength $item] > 1} {
			set head [lindex $item 0]
			switch -exact -- $head {
				"adjusted" {
					set cs [lindex [lrange $item 2 end] 0]
					foreach c $cs {
						set pn ""
						set y ""
						set x ""
						set z ""
						foreach p [lindex $c 2] {
							switch [lindex $p 0] {
								"id" {
									set pn [lindex [lindex [lindex $p 2] 0] 1]
								}
								"X" -
								"x" {
									set x [lindex [lindex [lindex $p 2] 0] 1]
								}
								"Y" -
								"y" {
									set y [lindex [lindex [lindex $p 2] 0] 1]
								}
								"Z" -
								"z" {
									set z [lindex [lindex [lindex $p 2] 0] 1]
								}
							}
						}
						if {$x != "" && $y != "" } { StoreCoord $pn $y $x }
						if {$z != ""} { StoreZ $pn $z }
					}
				}
				"orientation-shifts" {
					set os [lindex [lrange $item 2 end] 0]
					foreach o $os {
						set pn ""
						set oa ""
						set aoa ""
						foreach p [lindex $o 2] {
							switch [lindex $p 0] {
								"id" {
									set pn [lindex [lindex [lindex $p 2] 0] 1]
								}
								"adj" {
									set oa [lindex [lindex [lindex $p 2] 0] 1]
								}
								"approx" {
									set aoa [lindex [lindex [lindex $p 2] 0] 1]
								}
							}
						}
						if {$pn != "" && $oa != "" && $aoa != ""} {
							StoreOri $pn [Gon2Rad $oa] [Gon2Rad $aoa]
						}
					}
				}
				"fixed" -
				"approximate" -
				"cov-mat" -
				"original-index" -
				"observations" -
				"network-processing-summary" {
					continue
				}
				default {
					ProcessList $item
				}
			}
		}
	}
}


