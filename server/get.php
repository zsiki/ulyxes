<?php
/*
 * Sample script to collect data from ulyxes monitoring (httpwriter)
 *
 */

	//error_log(http_build_query($_REQUEST));

	$STR_TYPE = array('varchar', 'char', 'timestamp');
	include_once("config.php");

	if (isset($_REQUEST['east']) && isset($_REQUEST['north']) &&
		isset($_REQUEST['elev']) && isset($_REQUEST['datetime'])) {
		// coordinate record sent
		$table =$coo_table;
	} elseif (isset($_REQUEST['hz']) && isset($_REQUEST['v']) &&
		isset($_REQUEST['distance']) && isset($_REQUEST['datetime'])) {
		// totalstation observation record sent
		$table = $obs_table;
	} else {
		echo -1;
		error_log("Parameter error:" . http_build_query($_REQUEST));
		exit();
	}
	// $dbh = new PDO('pgsql:host=localhost;port=5432;dbname=ulyxes;user=postgres;password=qwerty');
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
	//error_log("insert into $table ($cols) values ($vals)");
	echo $i;	// number of lines affected (1)
?>
