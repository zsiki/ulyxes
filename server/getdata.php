<?php
/**
 * Ulyxes server side script to serve data to clients
 *
 * It is configured by a flexible json file (conf.json).
 * This script is invoked by GET/POST httprequest (AJAX) calls.
 * The POST or GET parameters of the request are:
 * type=points - get horizontal coordinates of the targets
 * type=buildings - get building or other polygons
 * type=dates - get min, max date of observations from database
 *  format - format specification for returned dates/datetimes
 * type=coords - get coordinata data within a period of time
 * 	point_names - comma separated list of point names to get data for
 * 	start_date - start date/datetime
 * 	end_date - end date/datetime
 * type=obs - get observations to targets from station
 *  station - station name/id
 * 	point_names - comma separated list of point names/ids to get data for
 * 	start_date - start date/datetime
 * 	end_date - end date/datetime
 * date - get start and end date of coordinate data
 *
 *	return JSON string with the requested data
 *  in case of points request:
 *  'xy': [{'point_name': '1230' , 'lng': '19.054391' , 'lat': '47.481882'},
 *         {'point_name': '1743' , 'lng': '19.056075' , 'lat': '47.481518'}]
 *
 * Suggested database schema (table and column names are configurable in 
 * conf.json
 *	points - WGS84 coordinates of points
 *		columns: gid, point_name, geom(point)
 *	coords - coordinates of points
 *		columns: point_name, date/datetime, east, north, elev
 *	buildings - additional polygons on map
 *		columns: gid, name, geom
 *
 * @author Zoltan Siki <siki (at) agt.bme.hu>
 * @package Ulyxes
 */

$conf = json_decode(file_get_contents("config.json"), true);

//connect to the database
$conn_str = sprintf("%s:host=%s;port=%d;dbname=%s",
	$conf["dbtype"], $conf["dbhost"], $conf["dbport"], $conf["dbname"]);
try {
	$conn = new PDO($conn_str, $conf["user"], $conf["pass"]);
} catch (PDOException $e) {
	echo "DB error: " . $e->getMessage() . "<br />";
	die ();
}

switch ($_REQUEST["type"]) {
	// create JSON string, array of point_name longitude latitude
	case "points" :
		$sql = sprintf("SELECT %s as id, ST_X(%s) as lng, ST_Y(%s) as lat FROM %s ORDER BY 1",
			$conf["point_id"], $conf["point_geom"], $conf["point_geom"],
			$conf["point_table"]);
		$buf = "{'xy':\n["; // start an array
		// go through all points
		foreach ($conn->query($sql) as $r) {
			$buf .= "{'point_id': '" . $r["id"] . "' ,
				'lng': '" . $r["lng"] . "' , 'lat': '" . $r["lat"] . "'},\n";
		}
		echo trim($buf, ",\n");
		echo "\n]\n}";
		break;

	// create JSON string of buildings polygons
	case "buildings" :
		$sql = sprintf("SELECT %s as name, ST_AsText(%s) as g, %s as id, ST_NPoints(%s) as n FROM %s",
			$conf["bld_name"], $conf["bld_geom"], $conf["bld_gid"],
			$conf["bld_geom"], $conf["bld_table"]);
		$buf = "{'buildings':\n[";
		foreach ($conn->query($sql) as $r) {
			// process WKT polygon description
			$p = preg_split('/,/',trim(substr($r["g"], strpos($r["g"], "((")), "()"));
			$buf .= "{'name': '" . $r["name"] . "' , 'points': [";
			for ($i=0; $i < $r["n"]; $i++) {
				$pi = preg_split('/ /', $p[$i]);
				//from WKT, delimited with space
				$buf .= "{'lng': '" . $pi[0] . "' , 'lat': '" . $pi[1] . "'},\n";
			}
			$buf = trim($buf, ",\n");
			$buf .= "\n]\n},";
		}
		echo trim($buf, ",\n");
		echo "\n]\n}";
		break;

	// create JSON string of coordinate data
	case "coords":
		$point_names = preg_split('/,/', $_REQUEST["point_names"]);
var_dump($point_names);
		$buf = "{'coords':\n[";
		$sql = sprintf("SELECT %s as id, %s as dt, %s as east, %s as north, %s as elev FROM %s WHERE %s=:name",
			$conf["coo_id"], $conf["coo_date"], $conf["coo_east"],
			$conf["coo_north"], $conf["coo_elev"], $conf["coo_table"],
			$conf["coo_id"]);
		if (!empty($_REQUEST["start_date"]) && !empty($_REQUEST["end_date"])) {
			$sql .= sprintf(" AND %s BETWEEN '%s' AND '%s'", 
				$conf["coo_date"], $_REQUEST["start_date"], $_REQUEST["end_date"]);
		}
		$sql .= " ORDER BY 2";
		$stmt = $conn->prepare($sql);
		if (! $stmt) {
			echo "<br/>prepare";
		}
		for ($i=0 ; $i < count($point_names) ; $i++) {
			$res = $stmt->bindParam(':name', $point_names[$i]);
			if (! $res) die ("Bind error");
			$res = $stmt->execute();
			if (! $res) die ("Execute error");
			$buf .= "{'point_id': '" . $point_names[$i] . "' , 'data': [\n";
			while (($r=$stmt->fetch(PDO::FETCH_ASSOC))) {
				$buf .= "{'dt': '" . $r["dt"] .
					"' , 'east': '" . $r["east"] . 
					"' , 'north':" . $r["north"] . 
					"' , 'elev':" . $r["elev"] . "'},\n";
			}
			$buf = trim($buf, ",\n");
			$buf .= "\n]\n},\n";
		}
		$buf = trim($buf, ",\n");
		$buf .= "\n]\n}"; //json ends
		echo $buf;
		$stmt->closeCursor();
		break;

	// create JSON string of observation data
	// TODO handle more stations
	case "obs":
		$point_names = preg_split('/,/', $_REQUEST["point_names"]);
var_dump($point_names);
		$buf = "{'obs':\n[";
		$sql = sprintf("SELECT %s as id, %s as dt, %s as hz, %s as v, %s as dist, %s as cincl, %s as lincl FROM %s WHERE %s=:name",
			$conf["obs_id"], $conf["obs_date"], $conf["obs_hz"],
			$conf["obs_v"], $conf["obs_dist"],
			$conf["obs_cincl"], $conf["obs_lincl"], $conf["obs_table"],
			$conf["obs_id"]);
		if (!empty($_REQUEST["start_date"]) && !empty($_REQUEST["end_date"])) {
			$sql .= sprintf(" AND %s BETWEEN '%s' AND '%s'", 
				$conf["obs_date"], $_REQUEST["start_date"], $_REQUEST["end_date"]);
		}
		$sql .= sprintf(" ORDER BY %s", $conf["obs_date"]);
		$stmt = $conn->prepare($sql);
		if (! $stmt) {
			echo "<br/>prepare";
		}
echo "<br />" . $sql;
		for ($i=0 ; $i < count($point_names) ; $i++) {
			//$res = $stmt->bindParam(':name', "'" . $point_names[$i] . "'");
			$res = $stmt->bindParam(':name', $point_names[$i]);
			if (! $res) die ("Bind error");
			$res = $stmt->execute();
			if (! $res) die ("Execute error");
			$buf .= "{'point_id': '" . $point_names[$i] . "' , 'data': [\n";
			while (($r=$stmt->fetch(PDO::FETCH_ASSOC))) {
				$buf .= "{'dt': '" . $r["dt"] .
					"' , 'hz': '" . $r["hz"] . 
					"' , 'v':" . $r["v"] . 
					"' , 'dist':" . $r["dist"] .
					"' , 'cincl':" . $r["cincl"] .
					"' , 'lincl':" . $r["lincl"] .
					"'},\n";
			}
			$buf = trim($buf, ",\n");
			$buf .= "\n]\n},\n";
		}
		$buf = trim($buf, ",\n");
		$buf .= "\n]\n}"; //json ends
		echo $buf;
		$stmt->closeCursor();
		break;

	// get min, max dates
	case "dates":
		$sql = sprintf("SELECT to_char(min(%s),'%s') AS sd, to_char(max(%s),'%s') AS ed FROM %s",
			$conf["coo_date"], $_REQUEST["format"], $conf["coo_date"],
			$_REQUEST["format"], $conf["coo_table"]);
		$stmt = $conn->query($sql, PDO::FETCH_ASSOC);
		$r=$stmt->fetch(PDO::FETCH_ASSOC);
		$buf = "{ 'sd':'" . $r["sd"] . "', 'ed':'" . $r["ed"] . "'}";
		echo $buf;
		break;

	default: die ("Incorrect parameters.");
}
pg_close();
?>
