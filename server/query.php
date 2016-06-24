<?php
/*
 * Sample script to query coordinates from ulyxes monitoring
 * (httpreader)
 *
 * query parameters:
 *    table: obs/coo/met observations/coordinates/met (optional), default coo
 *    plist: coma separated list of point ids (optional)
 *    ptyte: coma separated list of point types (optional)
 *    from:  starting datetime (optional)
 *    to:    end datetime (optional)
 *    ids:   query the list of unique point ids, do not use it with plist
 *    dates: query min/max dates
 *
 * With no parameters it returns the latest coordinates of all points
 */

	//error_log(http_build_query($_REQUEST));

	include_once("config.php");
	
	if (isset($_REQUEST['table']) && $_REQUEST['table'] == "obs") {
		$table = $obs_table;
		$cols = "$table.hz, $table.v, $table.distance";
	} elseif (isset($_REQUEST['table']) && $_REQUEST['table'] == "met") {
		$table = $met_table;
		$cols = "$table.temp, $table.pressure, $table.huminidity, $table.wettemp";
	} else {
		$table = $coo_table;
		$cols = "$table.east, $table.north, $table.elev";
	}
	$where = "";
	if (isset($_REQUEST['plist']) && strlen($_REQUEST['plist'])) {
		$pids = explode(",", $_REQUEST['plist']);
		// add single quote to point id list
		foreach ($pids as $key => $val) {
			$pids[$key] = "'$val'";
		}
		$pids = implode(",", $pids);
		$where = " WHERE $table.id in ($pids)";
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
			$where .= " $table.datetime >= '$from_d'";
		} else {
			echo -3;	// date format error
			exit();
		}
	}
	if (isset($_REQUEST['to']) && strlen(trim($_REQUEST['to']))) {
		if (preg_match($date_regexp, $_REQUEST['to']) ||
			preg_match($date_regexp1, $_REQUEST['to'])) {
			$to_d = $_REQUEST['to'];
			$where .= (strlen($where) ? " and" : " WHERE");
			$where .= " $table.datetime <= '$to_d'";
		} else {
			echo -4;	// date format error
			exit();
		}
	}
	$dbh = new PDO($conn_str);
	if (! $dbh) {
		echo -2;	// connection error
		exit();
	}
	// build query
	if (isset($_REQUEST['ids'])) {
		// get unique measure point ids
		$sql = "SELECT distinct  $table.id FROM $table " .
			"ORDER BY $table.id";
	} elseif (isset($_REQUEST['dates'])) {
		// get min/max date/time
		$sql = "SELECT min($table.datetime) AS sd, " .
		"max($table.datetime) AS ed FROM $table";
	} else {
		// get coordinates or observations
		$sql = "SELECT $table.id, $cols , $poi_table.code, $table.datetime " .
			"FROM $table INNER JOIN $poi_table " .
			"on ($table.id = $poi_table.id)";
		$sql .= $where;
		if (! isset($from_d) && ! isset($to_d)) {
			$sql .= (strlen($where) ? " and" : " WHERE");
			$sql .= " ($table.id, $table.datetime) " .
				"in (SELECT id, max(datetime) FROM $table GROUP BY id)";
		}
		$sql .= " ORDER BY $table.id, $table.datetime";
	}
//echo $sql . "<br>";
	echo "[";
	$sep = " ";
	foreach ($dbh->query($sql, PDO::FETCH_ASSOC) as $row) {
		echo $sep . json_encode($row);
		$sep = ", ";
	}
	echo " ]";
?>
