-- tables for Ulyxes monitoring
-- PostGIS version

-- drop previous version of tables
DROP TABLE IF EXISTS monitoring_inf;
DROP TABLE IF EXISTS monitoring_met;
DROP TABLE IF EXISTS monitoring_coo;
DROP TABLE IF EXISTS monitoring_obs;
DROP TABLE IF EXISTS monitoring_ref;

-- table for point coordinates in local reference system
-- reference coordinates given by the user
-- multiple reference can be given to the same point at different date
CREATE TABLE monitoring_ref (
	id varchar(50) NOT NULL,
	east double precision NOT NULL,
	north double precision NOT NULL,
	elev double precision NOT NULL,
	datetime timestamp NOT NULL,
	CONSTRAINT pkey_ref PRIMARY KEY (id, datetime)
);

-- table for point coordinates in local reference system
-- coordinates calculated by Ulyxes
CREATE TABLE monitoring_coo (
	id varchar(50) NOT NULL,
	east double precision NOT NULL,
	north double precision NOT NULL,
	elev double precision NOT NULL,
	datetime timestamp NOT NULL,
	CONSTRAINT pkey_coo PRIMARY KEY (id, datetime)
);

-- table for observations
-- polar observations made by Ulyxes
CREATE TABLE monitoring_obs (
	id varchar(50) NOT NULL,
	hz double precision NOT NULL,
	v double precision NOT NULL,
	distance double precision,
	crossincline double precision,
	lengthincline double precision,
    datetime timestamp NOT NULL,
	CONSTRAINT pkey_obs PRIMARY KEY (id, datetime)
);

-- table for meteorological observations at stations
-- id point id for observation
-- temp temperature celsius
-- pressure air pressure hpa
-- humidity
-- wettemp wet temperature
-- datetime of observation
CREATE TABLE monitoring_met (
	id varchar(50) NOT NULL,
	temp double precision NOT NULL,
	pressure double precision NOT NULL,
	humidity double precision,
	wettemp double precision,
    datetime timestamp NOT NULL,
	CONSTRAINT pkey_m PRIMARY KEY (id, datetime)
);

-- table for extra info
-- datetime of observation
-- nref number of reference points
-- nrefobs number of reference points measured
-- nmon number of monitoring points
-- nmonobs number of monitoring points measured
CREATE TABLE monitoring_inf (
    datetime timestamp NOT NULL,
    nref integer,
    nrefobs integer,
    nmon integer,
    nmonobs integer,
    maxincl double precision,
    std_east double precision,
    std_north double precision,
    std_elev double precision,
    std_ori double precision,
    CONSTRAINT pkey_i PRIMARY KEY (datetime)
);
