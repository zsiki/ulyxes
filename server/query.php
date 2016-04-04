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
		$where = " WHERE monitoring_coo.id in ($pids)";
	}
	if (isset($_REQUEST['ptype']) && strlen($_REQUEST['ptype'])) {
		$ptys = explode(",", $_REQUEST['ptype']);
		// add single quote to point id list
		foreach ($ptys as $key => $val) {
			$ptys[$key] = "'" . $val . "'";
		}
		$ptys = implode(",", $ptys);
		$where .= (strlen($where) ? " and" : " WHERE");
		$where .= " monitoring_poi.ptype in ($ptys)";
	}
	$date_regexp = '/^[12][0-9]{3}([-\.][0-9]{1,2}){2}\.?( [0-9]{1,2}(:[0-9]{1,2}){2})?$/';

	if (isset($_REQUEST['from'])) {
		if (preg_match($date_regexp, $_REQUEST['from'])) {
			$from_d = $_REQUEST['from'];
			$where .= (strlen($where) ? " and" : " WHERE");
			$where .= " monitoring_coo.datetime >= '$from_d'";
		} else {
			echo -3;	// date format error
			error_log("Date time format error");
			exit();
		}
	}
	if (isset($_REQUEST['to'])) {
		if (preg_match($date_regexp, $_REQUEST['to'])) {
			$to_d = $_REQUEST['to'];
			$where .= (strlen($where) ? " and" : " WHERE");
			$where .= " monitoring_coo.datetime <= '$to_d'";
		} else {
			echo -3;	// date format error
			error_log("Date time format error");
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
		$sql = "SELECT distinct  monitoring_coo.id ";
	} elseif (isset($_REQUEST['dates'])) {
		$sql = "SELECT min(monitoring_coo.datetime) AS sd, " .
		"max(monitoring_coo.datetime) AS ed ";
	} else {
		$sql = "SELECT monitoring_coo.id, monitoring_coo.east, " .
			"monitoring_coo.north, monitoring_coo.elev, monitoring_poi.code, " .
			"monitoring_coo.datetime ";
	}
	$sql .= "FROM monitoring_coo INNER JOIN monitoring_poi " .
			"on (monitoring_coo.id = monitoring_poi.id)";
	$sql .= $where;
	if (! isset($from_d) && ! isset($to_d) && ! isset($_REQUEST['dates'])) {
		$sql .= (strlen($where) ? " and" : " WHERE");
		$sql .= " (monitoring_coo.id, monitoring_coo.datetime) " .
				"in (SELECT id, max(datetime) FROM monitoring_coo " .
				"GROUP BY id) ORDER BY monitoring_coo.id";
	} elseif(! isset($_REQUEST['dates'])) {
		$sql .= " ORDER BY monitoring_coo.id, monitoring_coo.datetime";
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
