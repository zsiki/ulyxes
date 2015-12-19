-- tables for Ulyxes monitoring

-- drop previous version of tables
DROP TABLE IF EXISTS monitoring_coo;
DROP TABLE IF EXISTS monitoring_obs;
SELECT DropGeometryTable('monitoring_poi');
DROP TABLE IF EXISTS monitoring_poi;

-- table for points with web mercator geometry
CREATE TABLE monitoring_poi (
	id varchar(50) PRIMARY KEY
);
SELECT AddGeometryColumn('monitoring_poi', 'geom', 3857, 'POINT', 3);

-- table for point coordinates in local reference system
CREATE TABLE monitoring_coo (
	id varchar(50) NOT NULL REFERENCES monitoring_poi(id),
	east double precision NOT NULL,
	north double precision NOT NULL,
	elev double precision NOT NULL,
	datetime timestamp NOT NULL,
	CONSTRAINT pkey_coo PRIMARY KEY (id, datetime)
);

-- table for observations
CREATE TABLE monitoring_obs (
	id varchar(50) NOT NULL REFERENCES monitoring_poi(id),
	hz double precision NOT NULL,
	v double precision NOT NULL,
	distance double precision NOT NULL,
    datetime timestamp NOT NULL,
	CONSTRAINT pkey_obs PRIMARY KEY (id, datetime)
);
