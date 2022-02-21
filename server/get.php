<?php
/*
 * Sample script to collect data from ulyxes monitoring (httpwriter)
 *
 *  parameters to store measured (local) coordinates
 *    id: point id
 *    east: east coordinate
 *    north: north coordinate
 *    elev: elevation
 *    datetime: time stamp
 *
 *  parameters to store observations:
 *    id: point id
 *    hz: horizontal angle (WCB)
 *    v: zenith angle
 *    distance: slope distance
 *    datetime: time stamp
 *
 *  params to store initial, mapable (global) positions:
 *    id: point id
 *    east: east coordinate (or latitude)
 *    north: north cooridnate (or latitude)
 *    elev: elevation
 *    ptype: point type STA/FIX/MON
 *    code: target code ATR/RLA
 *
 *	parameters to store met data
 *    id: point id
 *	  temp: temperature
 *	  pressure: air pressure
 *	  huminidity: air huminidity
 *	  wettemp: wet temperature
 *    datetime: time stamp
 *	  
 *  config.php parameters
 *    conn_str: connection string
 *    coo_table: table name for local coordinates
 *    obs_table: table name for observations (total station)
 *    met_table: table name for meteorology data
 *    poi_table: table name for map coordinates
 */

	//error_log(http_build_query($_REQUEST));

	$STR_TYPE = array('varchar', 'char', 'bpchar', 'timestamp');
	include_once("config.php");

	if (! isset($_REQUEST['id'])) {
		echo -1;
		error_log("Parameter error: id missing" . http_build_query($_REQUEST));
		exit();
	}
	if ((isset($_REQUEST['east']) || isset($_REQUEST['north']) ||
		isset($_REQUEST['elev'])) && isset($_REQUEST['datetime'])) {
		// coordinate record sent
		$table =$coo_table;
	} elseif (isset($_REQUEST['hz']) && isset($_REQUEST['v']) &&
		isset($_REQUEST['distance']) && isset($_REQUEST['datetime'])) {
		// totalstation observation record sent
		$table = $obs_table;
	} elseif (isset($_REQUEST['east']) && isset($_REQUEST['north']) &&
		isset($_REQUEST['elev']) && isset($_REQUEST['ptype'])) {
		// poi record sent
		$table = $poi_table;
		$_REQUEST['geom'] = "ST_SetSRID(" .
			"ST_MakePoint(" . $_REQUEST['east'] . "," .
			$_REQUEST['north'] . "," . $_REQUEST['elev'] . "), 3857)";
	} elseif (isset($_REQUEST['datetime']) &&
		isset($_REQUEST['temp']) && isset($_REQUEST['pressure'])) {
		// met record sent
		$table = $met_table;
	} else {
		echo -1;
		error_log("Parameter error:" . http_build_query($_REQUEST));
		exit();
	}
	$dbh = new PDO($conn_str);
	if (! $dbh){
		echo -2;	// connection error
		error_log("Connection error: check connection string");
		exit();
	}
	// collect column names from table
	$rs = $dbh->query("SELECT * FROM $table LIMIT 0");
	for ($i = 0; $i < $rs->columnCount(); $i++) {
		$col = $rs->getColumnMeta($i);
	    $columns[] = $col['name'];
		$types[$col['name']] = $col['native_type'];
	}
	// collect column name and value pairs for insert
	$cols = "";		// columns in insert
	$vals = "";		// values in insert
	foreach ($_REQUEST as $key => $value) {
		if (in_array($key, $columns)) {
			$cols .= $key . ',';
			if (in_array($types[$key], $STR_TYPE)) {
				$vals .= "'" . $value . "',";
			} else {
				$vals .= $value . ',';
			}
		}
	}
	$cols = trim($cols, ',');
	$vals = trim($vals, ',');
	$i = $dbh->exec("insert into $table ($cols) values ($vals)");
	// error_log("insert into $table ($cols) values ($vals)");
	echo $i;	// number of lines affected (1)
?>
