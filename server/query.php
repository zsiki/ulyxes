<?php
/*
 * Sample script to query coordinates from ulyxes monitoring
 * (httpreader)
 *
 * query parameters:
 *    plist: coma separated list on point ids
 *    ptyte: coma separated list of point types
 *    from:  starting datetime (optional)
 *    to:    end datetime (optional)
 *    ids:   query the list of unique point ids, do not use it with plist
 *    dates: query min/max dates
 *
 * With no parameters it returns the latest coordinates of all points
 */

	//error_log(http_build_query($_REQUEST));

	include_once("config.php");
	
	$where = "";
	if (isset($_REQUEST['plist']) && strlen($_REQUEST['plist'])) {
		$pids = explode(",", $_REQUEST['plist']);
		// add single quote to point id list
		foreach ($pids as $key => $val) {
			$pids[$key] = "'$val'";
		}
		$pids = implode(",", $pids);
		$where = " WHERE $coo_table.id in ($pids)";
	}
	if (isset($_REQUEST['ptype']) && strlen($_REQUEST['ptype'])) {
		$ptys = explode(",", $_REQUEST['ptype']);
		// add single quote to point id list
		foreach ($ptys as $key => $val) {
			$ptys[$key] = "'" . $val . "'";
		}
		$ptys = implode(",", $ptys);
		$where .= (strlen($where) ? " and" : " WHERE");
		$where .= " $poi_table.ptype in ($ptys)";
	}
	// ANSI DATE
	$date_regexp = '/^[12][0-9]{3}([-\.][0-9]{1,2}){2}\.?( [0-9]{1,2}(:[0-9]{1,2}){2})?$/';
	// US DATE
	$date_regexp1 = '/^([0-9][0-9]?\/){2}[12][0-9]{3}$/';

	if (isset($_REQUEST['from']) && strlen(trim($_REQUEST['from']))) {
		if (preg_match($date_regexp, $_REQUEST['from']) ||
			preg_match($date_regexp1, $_REQUEST['from'])) {
			$from_d = $_REQUEST['from'];
			$where .= (strlen($where) ? " and" : " WHERE");
			$where .= " $coo_table.datetime >= '$from_d'";
		} else {
			echo -3;	// date format error
			error_log("Date time format error from");
			exit();
		}
	}
	if (isset($_REQUEST['to']) && strlen(trim($_REQUEST['to']))) {
		if (preg_match($date_regexp, $_REQUEST['to']) ||
			preg_match($date_regexp1, $_REQUEST['to'])) {
			$to_d = $_REQUEST['to'];
			$where .= (strlen($where) ? " and" : " WHERE");
			$where .= " $coo_table.datetime <= '$to_d'";
		} else {
			echo -4;	// date format error
			error_log("Date time format error to");
			exit();
		}
	}
	$dbh = new PDO($conn_str);
	if (! $dbh) {
		echo -2;	// connection error
		error_log("Connection error: check connection string");
		exit();
	}
	// build query
	if (isset($_REQUEST['ids'])) {
		$sql = "SELECT distinct  $coo_table.id FROM $coo_table " .
			"ORDER BY $coo_table.id";
	} elseif (isset($_REQUEST['dates'])) {
		$sql = "SELECT min($coo_table.datetime) AS sd, " .
		"max($coo_table.datetime) AS ed FROM $coo_table";
	} else {
		$sql = "SELECT $coo_table.id, $coo_table.east, " .
			"$coo_table.north, $coo_table.elev, $poi_table.code, " .
			"$coo_table.datetime " .
			"FROM $coo_table INNER JOIN $poi_table " .
			"on ($coo_table.id = $poi_table.id)";
		$sql .= $where;
		if (! isset($from_d) && ! isset($to_d)) {
			$sql .= (strlen($where) ? " and" : " WHERE");
			$sql .= " ($coo_table.id, $coo_table.datetime) " .
				"in (SELECT id, max(datetime) FROM $coo_table " .
				"GROUP BY id)";
		}
		$sql .= " ORDER BY $coo_table.id, $coo_table.datetime";
	}
//echo $sql . "<br>";
	$rs = $dbh->query($sql);
	echo "[";
	$sep = " ";
	foreach ($dbh->query($sql, PDO::FETCH_ASSOC) as $row) {
		echo $sep . json_encode($row);
		$sep = ", ";
	}
	echo " ]";
?>
