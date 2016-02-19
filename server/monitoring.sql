-- tables for Ulyxes monitoring

-- drop previous version of tables
DROP TABLE IF EXISTS monitoring_coo;
DROP TABLE IF EXISTS monitoring_obs;
SELECT DropGeometryTable('monitoring_poi');
DROP TABLE IF EXISTS monitoring_poi;

-- table for points with web mercator geometry
-- each point must be inserted into this table
-- it is used to display points on web map (EPSG:3857)
-- ptype can be FIX/STA/MON for fix points, stations, monitoring points
CREATE TABLE monitoring_poi (
	id varchar(50) PRIMARY KEY,
	ptype char(3) NOT NULL DEFAULT 'MON' CHECK (ptype in ('FIX','STA','MON')),
);
SELECT AddGeometryColumn('monitoring_poi', 'geom', 3857, 'POINT', 3);

-- table for point coordinates in local reference system
-- coordinates calculated by Ulyxes
CREATE TABLE monitoring_coo (
	id varchar(50) NOT NULL REFERENCES monitoring_poi(id),
	east double precision NOT NULL,
	north double precision NOT NULL,
	elev double precision NOT NULL,
	datetime timestamp NOT NULL,
	CONSTRAINT pkey_coo PRIMARY KEY (id, datetime)
);

-- table for observations
-- polar observations made by Ulyxes
CREATE TABLE monitoring_obs (
	id varchar(50) NOT NULL REFERENCES monitoring_poi(id),
	hz double precision NOT NULL,
	v double precision NOT NULL,
	distance double precision NOT NULL,
    datetime timestamp NOT NULL,
	CONSTRAINT pkey_obs PRIMARY KEY (id, datetime)
);
