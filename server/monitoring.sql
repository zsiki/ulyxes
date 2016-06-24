-- tables for Ulyxes monitoring

-- drop previous version of tables
DROP TABLE IF EXISTS monitoring_pgr;
DROP TABLE IF EXISTS monitoring_grp;
DROP TABLE IF EXISTS monitoring_met;
DROP TABLE IF EXISTS monitoring_coo;
DROP TABLE IF EXISTS monitoring_obs;
SELECT DropGeometryTable('monitoring_poi');
DROP TABLE IF EXISTS monitoring_poi;

-- table for points with web mercator geometry
-- each point must be inserted into this table
-- it is used to display points on web map (EPSG:3857)
-- ptype can be FIX/STA/MON for fix points, stations, monitoring points
-- code can be ATR/RLA/PR/RL/ORI
-- pc additive constant for distance measurement
CREATE TABLE monitoring_poi (
	id varchar(50) PRIMARY KEY,
	ptype char(3) NOT NULL DEFAULT 'MON' CHECK (ptype in ('FIX','STA','MON')),
	code char(4) NOT NULL DEFAULT 'ATR' CHECK (code in ('ATR', 'PR', 'ORI', 'RL', 'RLA')),
	pc float NOT NULL DEFAULT 0
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
	distance double precision,
	crossincline double precision,
	lengthincline double precision,
	face int NOT NULL check (face in (1, 2, 0)),
    datetime timestamp NOT NULL,
	CONSTRAINT pkey_obs PRIMARY KEY (id, datetime, face)
);

-- table for meteorological observations at stations
-- id point id for observation
-- temp temperature celsius
-- pressure air pressure hpa
-- huminidity
-- wettemp wet temperature
-- datetime of observation
CREATE TABLE monitoring_met (
	id varchar(50) NOT NULL REFERENCES monitoring_poi(id),
	temp double precision NOT NULL,
	pressure double precision NOT NULL,
	huminidity double precision,
	wettemp double precision,
    datetime timestamp NOT NULL,
	CONSTRAINT pkey_m PRIMARY KEY (id, datetime)
);

-- table for point groups
-- id name of group
-- remark optional description of group
CREATE TABLE monitoring_grp (
	id varchar(50) PRIMARY KEY,
	remark varchar(100)
);

-- table for point group connections
-- gid group id
-- pid point id
CREATE TABLE monitoring_pgr (
	gid varchar(50) NOT NULL REFERENCES monitoring_grp(id),
	pid varchar(50) NOT NULL REFERENCES monitoring_poi(id),
	CONSTRAINT pkey_pgr PRIMARY KEY (gid, pid)
);

