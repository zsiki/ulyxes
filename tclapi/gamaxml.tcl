proc xml2list xml {
# skip <? xml ... ?> and <!DOCTYPE >
	regsub {^[ \n\r\t]*<\?xml .*\?>[ \t\n\r]*<!DOCTYPE +gama-.* +SYSTEM \"gama-.*\.dtd\">} $xml "" xml
# remove all html like comment start and end tag <!-- ... -->
	regsub -all -- {<!--} $xml "" xml
	regsub -all -- {-->} $xml "" xml

     regsub -all {>\s*<} [string trim $xml " \n\t<>"] "\} \{" xml
     set xml [string map {> "\} \{#text \{" < "\}\} \{"}  $xml]
#puts $xml
     set res ""   ;# string to collect the result
     set stack {} ;# track open tags
     set rest {}
     foreach item "{$xml}" {
         switch -regexp -- $item {
            ^# {append res "{[lrange $item 0 end]} " ; #text item}
            ^/ {
                regexp {/(.+)} $item -> tagname ;# end tag
				set tagname [string trim $tagname]
                set expected [lindex $stack end]
                if {$tagname!=$expected} {error "$item != $expected"}
                set stack [lrange $stack 0 end-1]
                append res "\}\} "
          }
            /$ { # singleton - start and end in one <> group
               regexp {([^ ]+)( (.+))?/$} $item -> tagname - rest
               set rest [lrange [string map {= " "} $rest] 0 end]
               append res "{$tagname [list $rest] {}} "
            }
            default {
               set tagname [lindex $item 0] ;# start tag
               set rest [lrange [string map {= " "} $item] 1 end]
               lappend stack $tagname
               append res "\{$tagname [list $rest] \{"
            }
         }
         if {[llength $rest]%2} {error "att's not paired: $rest"}
     }
     if {[llength $stack]} {error "unresolved: $stack"}
     string map {"\} \}" "\}\}"} [lindex $res 0]
 }

#---- Now that this went so well, I'll throw in the converse:

 proc list2xml list {
    switch -- [llength $list] {
        2 {lindex $list 1}
        3 {
            foreach {tag attributes children} $list break
            set res <$tag
            foreach {name value} $attributes {
                append res " $name=\"$value\""
            }
            if {[llength $children]} {
                append res >
                foreach child $children {
                    append res [list2xml $child]
                }
                append res </$tag>
            } else {append res />}
        }
        default {error "could not parse $list"}
    }
 }

#-------------------------------------------------------------------------------
#	-- ProcessList
#	Read coordinates and orientations from list and return
#
#-------------------------------------------------------------------------------
proc ProcessList {l} {
	global stn stnx stny stnz
	global oa
	foreach item $l {
		if {[llength $item] > 1} {
			set head [lindex $item 0]
			switch -exact -- $head {
				"adjusted" {
					set cs [lindex [lrange $item 2 end] 0]
					foreach c $cs {
						foreach p [lindex $c 2] {
							switch [lindex $p 0] {
								"id" {
									set pn [lindex [lindex [lindex $p 2] 0] 1]
								}
								"X" -
								"x" {
									if {$pn == $stn} {
										set stnx [lindex [lindex [lindex $p 2] 0] 1]
									}
								}
								"Y" -
								"y" {
									if {$pn == $stn} {
										set stny [lindex [lindex [lindex $p 2] 0] 1]
									}
								}
								"Z" -
								"z" {
									if {$pn == $stn} {
										set stnz [lindex [lindex [lindex $p 2] 0] 1]
									}
								}
							}
						}
					}
				}
				"orientation-shifts" {
					set os [lindex [lrange $item 2 end] 0]
					foreach o $os {
						foreach p [lindex $o 2] {
							switch [lindex $p 0] {
								"id" {
									set pn [lindex [lindex [lindex $p 2] 0] 1]
								}
								"adj" {
									if {$pn == $stn} {
										set oa [lindex [lindex [lindex $p 2] 0] 1]
									}
								}
								"approx" {
									if {$pn == $stn} {
										set aoa [lindex [lindex [lindex $p 2] 0] 1]
									}
								}
							}
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

#-------------------------------------------- now testing:
#set f [open "../gama-1.8.01/examples/out.xml" r]
#set test [read $f]
#puts $test
#puts [set res [xml2list $test]]
