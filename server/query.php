<?php
/*
 * Sample script to query  latest coordinates from ulyxes monitoring
 * (httpreader)
 *
 * query parameters:
 *    plist: coma separated list on point ids
 *    ptyte: coma separated list of point types
 *
 */

	//error_log(http_build_query($_REQUEST));

	include_once("config.php");
	
	$where = "";
	if (isset($_REQUEST['plist']) && strlen($_REQUEST['plist'])) {
		$pids = explode(",", $_REQUEST['plist']);
		// add single quote to point id list
		foreach ($pids as $key => $val) {
			$pids[$key] = "'" . $val . "'";
		}
		$pids = implode(",", $pids);
		$where = " WHERE monitoring_coo.id in (" .  $pids . ")";
	}
	if (isset($_REQUEST['ptype']) && strlen($_REQUEST['ptype'])) {
		$ptys = explode(",", $_REQUEST['ptype']);
		// add single quote to point id list
		foreach ($ptys as $key => $val) {
			$ptys[$key] = "'" . $val . "'";
		}
		$ptys = implode(",", $ptys);
		if (strlen($where)) {
			$where .= " and monitoring_poi.ptype in (" . $ptys . ")";
		} else {
			$where = " WHERE monitoring_poi.ptype in (" . $ptys . ")";
		}
	}
	// $dbh = new PDO('pgsql:host=localhost;port=5432;dbname=ulyxes;user=postgres;password=qwerty');
	$dbh = new PDO($conn_str);
	if (! $dbh) {
		echo -2;	// connection error
		error_log("Connection error: check connection string");
		exit();
	}
	// build query
	$sql = "SELECT monitoring_coo.id, monitoring_coo.east, " .
			"monitoring_coo.north, monitoring_coo.elev " .
			"FROM monitoring_coo INNER JOIN monitoring_poi " .
			"on (monitoring_coo.id = monitoring_poi.id)";
	if (strlen($where)) {
		$sql .= $where . " and (monitoring_coo.id, monitoring_coo.datetime) " .
				"in (SELECT id, max(datetime) FROM monitoring_coo " .
				"GROUP BY id)";
	} else {
		$sql .= " WHERE and (monitoring_coo.id, monitoring_coo.datetime) in (SELECT id, max(datetime) FROM monitoring_coo)";
	}
// echo $sql;
	$rs = $dbh->query($sql);
	echo "[ ";
	foreach ($dbh->query($sql, PDO::FETCH_ASSOC) as $row) {
		echo json_encode($row);
	}
	echo " ]";
?>
