.. ulyxes_user_documentation

######
ULYXES
######
User's Guide
------------


.. topic:: Overview

    This documentation stands as an User Manual of `Ulyxes <http://www.agt.bme.hu/ulyxes/>`_ system. The main aim of it is to represent the Ulyxes system and describe the usage of it with given examples and tutorials.



    :Date: 2020-01-04
    :Authors: **Daniel Moka** <mokabme@gmail.com>, **Zoltan Siki** <siki@agt.bme.hu>
    :Version: 1.0


.. contents:: 
    :depth: 5

.. sectnum::

.. raw:: LaTeX

   \newpage


Introduction
############

Ulyxes is an open source project to drive Robotic Total Stations (RTS) and
other location aware sensors and publish observation results on web based maps 
(GPL 2). The name of Ulyxes come from the Greek Odysseus who was a legendary
Greek king of Ithaca island. Or it can be resolved as Ultimate Y X Estimation
System.

The first aim of the project is to create a framework to drive different 
location aware sensors from a computer, furthermore publish the data on the
Internet. The project is based on several open source projects and programming
languages. The overview of the system can been seen on the following figure:

.. figure:: img/ulyxes_overview.png
    :align: center
    :scale: 74
    :alt: Overview Ulyxes

    Ulyxes system overview

System Divisions
################

Publisher Interface
*******************

The first part of the system is the publishing interface where the measurement
results and the related analysis are published in the form of maps, tables and 
graphs with the associated Geo-spatial visualization. The interface works within
an Internet browser (e.g. Mozzila Firefox or Google Chrome) which supports to
run Javascript. As for operation system, the interface is cross-platform so it
can be used on any operation system.

Servers
*******

There are number of open source server projects contribute the back-end
operation of the system. In order to store the observation data in databases,
Ulyxes uses PostgreSQL/PostGIS object relational database. The data flow from 
the database to the web-server is solved by using PHP scriptins or MapServer. 
The webserver is driven and supported by the Apache Web Server. In addition, 
other possibilities and alternatives can be used to solve the server side works,
for example a Map Server (Web Map Service - WMS) can be also an effective 
solution.


Sensor Managers
***************

The system contains two different API independent from each other: the 
**TclAPI** and the **PyAPI**. The TclAPI is the old and its development is 
finished (depricated). Tha PyAPI is the new and actively developed.

TclAPI (depricated)
===================

The TclAPI consist of a couple of Tcl (Tool Command Language) files/procs which
give a higher level interface to drive RTSs and GPSs from computer. The TclAPI 
is released under GNU GPL V2.0. This API is obsolate and no new functionality
will be added. It has been already tested with the following type of
instruments:

    * Leica TCA1800 
    * Leica TPS120x
    * Leica TPS110x 
    * Leica DNA03 
    * Trimble 550x 
    * Garmin GPS18 
    * Leica GPS 500 

Specification
^^^^^^^^^^^^^

*Supported OS (Operating System):*

    * Linux (probably any distro, tested on Fedora and Ubuntu) 
    * Windows XP/Vista/7 (32 and 64 bit) (tested on XP/7) 
    * any other OS with Tcl 8.3 or newer installed (not tested)

|

*Requirements:*

    * Tcl (Tool Command Language) 8.3 or newer must be installed 
    * at least one serial port or USB to serial converter (tested with Prolific)
    * serial cabel to connect the instrument to the computer 

How to install Tcl/Tk
^^^^^^^^^^^^^^^^^^^^^

*Linux (Ubuntu/Debian):*

    1. Open a terminal
    2. Type: *sudo apt-get install tk8.5 tcl8.5* 

.. note::  The apt-get command is a powerful command-line tool, performing such functions as installation of new software packages, upgrade of existing, so on. For more info, visit: https://help.ubuntu.com/lts/serverguide/apt-get.html

*Windows:*

These steps can be also found at http://trac.osgeo.org/osgeo4w/

    1. Download the 32bit (http://www.activestate.com/activetcl/downloads) or 
       the 64bit installer
    2. Run the installer

..Note:
    * OSGeo4W installer also install Tcl/Tk, you can use it also

How to install TclAPI
^^^^^^^^^^^^^^^^^^^^^

The TclAPI is a part of Ulyxes system. In order to install the API, the whole Ulyxes project folder has to be installed.

*If you have git client installed on your machine:*

    1. Open a terminal
    2. Go to or make the desired “MyFolder” you want to install Ulyxes/TclAPI
    3. Clone the Ulyxes Git directory, so type: git clone https://github.com/zsiki/ulyxes.git
    4. The TclAPI can be found at: “MyFolder/Ulyxes/TclAPI”


*If you have no git client on your machine:*

    #. Open your browser
    #. Navigate to `Ulyxes Github page <https://github.com/zsiki/ulyxes>`_ 
    #. Press the **Download ZIP** button (right side, down)
    #. Uncompress the downloaded file to a suitable directory

.. figure:: img/uly_git.png
    :align: right
    :width: 195px
    :height: 140px
    :scale: 330
    :alt: Overview Ulyxes

    Download Ulyxes ZIP folder

PyAPI
=====

First of all the TclAPI is only able to control total stations and GPSs. The
usage of such instruments does not raise controversies, however other sensors
(i.e. web-cameras or Miro-Electro-Mechanical (MEMS) Sensors) can be also 
effectively used for certain motion monitoring tasks. Furthermore, as for the 
long term tasks the changes of the atmosphere influence our measurements, 
therefore meteorological sensors should be used to determine the meteorological 
elements which with the total stations can be maintained. To easily integrate 
such a different kind of instruments to the system, we decided to rethink our 
system so the PyAPI was created which is based on Python object oriental
language (OOP). Python is a general purpose high-level programming language
that provides a very fast development and testing tools for the user. It has 
countless additional library which can significantly contribute and help the 
programmers' work. Last but not least the biggest commercial and open source 
applications (QGIS, ArcGIS) have selected Python for development tool. (For 
more info, visit https://www.python.org/)

PyAPI is an Application Programming Interface (API) provides several classes to
handle different sensors e.g. Totalstations, NMEA GNSS receivers, MEMS sensors,
web-cameras. The API still only has a beta version.

Specification
^^^^^^^^^^^^^

*Supported OS (Operating System):*

    * Linux (probably any distro, tested on Fedora, Ubuntu, Raspbian) 
    * Windows XP/Vista/7/8/10 (32 and 64 bit) (tested on XP/7/10) 
    * any other OS with Python 2.7.x/3.x installed (not tested)

*Requirements:*

    * Python 2.7.x/3.x
    * at least one serial port or USB to serial converter (tested with Prolific)
    * serial cabel to connect the instrument to the computer 
    * I2C interface for MEMS (Raspberry PI)

How to install Python 3.x
^^^^^^^^^^^^^^^^^^^^^^^^^

See: https://realpython.com/installing-python/

Required Python modules
^^^^^^^^^^^^^^^^^^^^^^^

*Standard modules*:

    * datetime
    * json
    * logging
    * math
    * os
    * re
    * socket
    * sys
    * tempfile
    * time
    * urllib
    * xml.etree.ElementTree
    
*Extra modules*:

    * pyserial
	* pybluez
    * smbus
    * sqlite3
    * wifi 
    * numpy
    * opencv


*External dependencies*:
    * GNU Gama
	* sqlite3, spatialite-bin

How to install PyAPI
^^^^^^^^^^^^^^^^^^^^

The PyAPI is a part of Ulyxes system. In order to install the API, the whole Ulyxes project folder has to be installed.

*Linux*

    1. Open a terminal
    2. Go to or make the desired “MyFolder” you want to install Ulyxes/PyAPI
    3. Clone the Ulyxes Git directory, so type: git clone https://github.com/zsiki/ulyxes.git
    4. The TclAPI can be found at: “MyFolder/Ulyxes/PyAPI”

*Windows*

    1. Go to https://github.com/zsiki/ulyxes.git Ulyxes Git website 
    2. On the website, you can find a “Download ZIP” button at the bottom right part
    3. The downloaded Ulyxes directory will contain the PyAPI



PyAPI Modules
#############

(For more detailed information and sources codes about modules of PyAPI, please visit the `official developer documentation <http://www.agt.bme.hu/ulyxes/pyapi_doc/>`_ of PyAPI  )

.. figure:: img/abstraction.png
    :align: center
    :alt: Overview Ulyxes

    Sensor Abstraction

|

*There are three groups of modules used by PyAPI:*

PyAPI Object-Model modules
**************************

The first group consist of modules which build up the logical model between sensors, interfaces and the writer.

Independent modules
*******************

angle.py
========

This module stands for storing angle value of numbers in radian internally. Using this class the angle conversions can be easily done. 

|

Supported angle units:

    * RAD  radians (e.g. 1.54678432)
    * DMS sexagesimal (Degree-Minit-Second, e.g. 123-54-24)
    * DEG decimal degree (e.g. 25.87659)
    * GON gradian whole circle is 400g (e.g. 387.7857)
    * NMEA ddmm.mmmm used in NMEA sentences (e.g. 47.338765)
    * PDEG pseudo sexagesimal (e.g. 156.2745 = 156-27-45)
    * SEC sexagesimal seconds
    * MIL mills the whole circle is 6400 mills

|

.. code:: python

    #Create Angle object with the given value and unit
    a1 = Angle("152-23-45", "DMS")
    #Convert a1 "angle" object to supported units
    for u in ['RAD', 'DMS', 'GON', 'NMEA', 'DEG', 'PDEG', 'MIL']:
        print (a1.GetAngle(u))


Readers
=======

reader.py is the base class for all readers (virtual).

configreader.py
^^^^^^^^^^^^^^^

TODO

csvreader.py
^^^^^^^^^^^^

Class to read csv file, first line must contain field names.
Default separator is semicolon (;).

.. code:: python

    # create a csvreader object
    cr = CsvReader('test', 'test.csv')
    # load the whole file into a list
    lines = cr.Load()

filereader.py
^^^^^^^^^^^^^

Class to read file. It is mostly used as a base class for other readers
loading information from file.

.. code:: python
    
    # create a filereader object
    fr = FileReader('test', 'test.txt')
    # read and print the next line
    print (fr.GetNext())

georeader.py
^^^^^^^^^^^^

Class to read GeoEasy geo or coo files. Data are loaded into a list of
dictionaries. Possible keys in dictionaries:

* station - station ID
* ih - instrument height
* code - additional textual information to point
* id - target ID
* th - target height
* hz - horizontal direction
* v - zenith angle
* distance - slope distance
* hd - horizontal distance
* pc - prism constant
* north - north coordinate
* east - east coordinate
* elev - elevation
* datetime - date and time of observation
* faces - number of faces

Creating a new GeoReader instance a file name and a filter can be specified.
The filter is a list of the keys above. Only those lines are kept where all
filter keys are present. One can use a filter to load only 3D points from
the coordinate list.

.. code:: python
    
	# load 3D points from a GeoEasy coo file
	g = GeoReader(fname='your_file.coo', filt=['east', 'north', 'elev'])
	m = g.Load()	# load 3D points
	print(m)

httpreader.py
^^^^^^^^^^^^^

Read data from a remote web server using HTTP protocol and server side service
for POST/GET requests.

TODO

jsonreader.py
^^^^^^^^^^^^^

TODO

sqlitereader.py
^^^^^^^^^^^^^^^

Load coordinates or observations from a spatialite database.
TODO

External Python modules
***********************

Logging
=======
This module defines functions and classes which implement a flexible event
logging system for applications and libraries.

For more information, please visit the `official Logging documentation <https://docs.python.org/2/library/logging.html>`_.

Pyusb
=====
The PyUSB module provides for Python easy access to the host machine's Universal Serial Bus (USB) system.

For more information, please visit the `official PyUSB Github page <https://github.com/walac/pyusb>`_.

Pyserial
========
This module encapsulates the access for the serial port. It provides backends
for Python running on Windows, Linux, BSD (possibly any POSIX compliant system),
Jython and IronPython (.NET and Mono).

For more information, please visit the `official PySerial documentation <http://pyserial.sourceforge.net/pyserial.html#overview>`_.

Smbus
=====

TODO

Cv2/cv (OpenCV)
===============

OpenCV (Open Source Computer Vision Library: http://opencv.org) is an
open-source BSD-licensed library that includes several hundreds of computer
vision algorithms.

For more information, please visit the `official OpenCV documentation <http://docs.opencv.org/modules/core/doc/intro.html>`_.


PyAPI Tutorials
###############

Most of the Python modules contain a unit test part at the end (after
the if __name__ == "__main__":). These are also usage examples.

Use of the SerialInterface
**************************

The SearialIface class can be used alone to drive an instrument through the
serial chanel or as a building block of an Instrument instance.

.. code:: python

    from serialiface import SerialIface
    si = SerialIface('test', 'COM1')
    si.Send('%R1Q,9028:0,0,0')
    %R1P,0,0:

Sensor Creation
***************

All the sensors (instruments) are inherited from the Instrument virtual base 
class. A sensor consists of three building blocks:

* measure unit
* interface (communication)
* writer (saving observed data), optional

.. code:: python

    import logging
	from leicatps1200 import LeicaTPS1200
	from serialiface import SerialIface
    from echowriter import EchoWriter
    logging.getLogger().setLevel(logging.DEBUG)
    mu = LeicaTPS1200()
    iface = SerialIface("rs-232", "/dev/ttyUSB0")
    wrt = EchoWriter()
    ts = TotalStation("Leica", mu, iface, wrt)
    ts.SetEDMMode(ts.measureUnit.edmModes['RLSTANDARD'])
    ts.Move(Angle(90, 'DEG'), Angle(85, 'DEG'))
    ts.Measure()
    print (ts.GetMeasure())

PyAPPS Applications Tutorials
#############################

MeasureToPrism
**************

Repeated robotic totalstation observations to a single (slowly moving) point. 
It has several modes:

* 0 - determine horizontal movement of a point using reflectorless (RL) EDM
* 1 - determine movement ofa slowly moving prism
* 2 - determine vertical movement of a prims (supposing horizontal distance not changed
* 3 - determine vertical movement of a moving prism on a car/machine, we suppose horizontal distance is not changed
* 4 - determine 3D movement of a moving prism
* 5 - measure if prism stop moving for few seconds (stop and go) obsevations

Command line parameters:

* Sensor type 1100/1800/1200
* Mode 0-5
* EDM mode FAST/STANDARD
* serial port
* output file

Measurematrix
*************

An application to scan a region with given angle steps. Parameters are given in
the command line, the corners of the region are given by targeting manually on 
the points.
Commands line parameters are positional:

# number of horizontal intervals in the region
# number of vertical intervals in the region
# sensor (total station) type
# serial port
# output file

After starting the program the user have to target on the lower left corner of 
the region and the upper right corner of the region. The automatic observations
are started then. If no output file given the observations are written to the 
standard output.

NMEA_demo
*********

A simple demo application to read NMEA GGA sentences from GNSS receiver in an
infinite loop.

Horizsection
************

Scan horizontally around the total station with a given angle step in several
horizontal sections.

Section
*******

Scan in an arbitrary plain aroun the total station with a given angle step.

Monitoring
**********

This block consist of several apps to solve simple tasks for monitoring.

- *filemaker* creates an input file for monitoring using manual targeting
- *filegen* creates an input file for monitoring from coordinates automaticly
- *coomaker* creates a GeoEasy format input file for monitoring using manual targeting
- *blindorientation* searches for a prism from a known station and calculates orientation angle
- *freestation* calculates station coordinates and orientation using GNU gama
- *robot* makes automatic observation using a file from FileMaker or FileGen
- *robotplus* complex monitoring application using FileGen, Blindorientation, FreeStation and Robot

FileMaker
=========

It is a simple interactive app to create input file for monitoring observations.
First set up the total station on a known point and set the orientation.

Usage: filemaker.py output_file [sensor] [serial_port]

Start the application. Two types of output files can be generated, CSV dump 
(.dmp) or GeoEasy (.geo) file.
First it will prompt for the id of the station and the station coordinates.

For each target points the id and mode must be entered.

Target modes:

- ATR*n* use automatic targeting, n is prism type id (1/2/3/...)
- PR*n* prism with manual targeting
- RL reflectorless distance with manual targeting
- RLA automatic reflectorless ditance measurement to given direction
- OR orientation direction, manual targeting, no distance

.. NOTE::
   Generated output file cannot be used for Blindorientation because
   distance missing!

FileGen
=======

A simple application to create input observations file for robot.py. 
The input is a coordinate list in GeoEasy coo or CSV format. The output is a 
GeoEasy geo or DMP file with bearings, zenith angles and distances from
the station to the points in the coordinate list.

Usage: filegen.py input_coo_file output_obs_file station_id instrument_height

Tha station_id is optional, if not given the first point in the coordinate list
is considered as the station. Instrument height is also optional, the default
value is 0.

CooMaker
========

A simple application to create coordinate and observation data for robot.py
and robotplus.py. User have to set up and orient the total station on the 
station and observe targets.

Usage: coomaker.py output_file sensor port

- output file: two files are created with the same name extensions .geo/.coo
- sensor: total station type 1100/1800/1200/5500
- port: serial port e.g. COM1 or /dev/ttyUSB0

Further data are given at the prompt of the program.

FreeStation
===========

An application to calculate free station from observations and coordinates.
A least squaers estimation is used based on GNU gama.

Blindorientation
================

This apllication tries to solve orientation. It searches for prisms.
First tries if a prism is in the view of telescope using Automatic Target Recognition (ATR).
If a target found it checks the distance and the zenith angle to find the 
target in the coordinate list and set the orientation angle on the 
instrument.

If no target found in the actial view it rotates the instrument to the first 
target supposing oriented instrument and set the orientation angle.

Finally it starts search using Power Search if it is available on the total 
station or starts a long searching algorithm.

Robot
=====

Sample application of Ulyxes PyAPI to measure a serie of points.

Usage: robot.py input_file output_file sensor port retry delay met met_addr met_par

Positional command line parameters:

- input_file: input file with directions .geo or .dmp
- output_file: output file with observations default stdout
- sensor: tcra1103/1100/tca1800/1800/tps1201/1200, default 1200
- port: serial port, default COM1
- retry: number of retry if target not found, default 3
- delay: delay between retries default 0
- met: name of met sensor BMP180/webmet, default None
- met_addr address of met sensor, i2c addres for BMP180 or internet address of webmet service
- met_par: parameters for webmet sensor

Input file is a GeoEasy geo file or a dmp (can be created by filemaker.py
or filegen.py).
Sample geo file::

    {2 S2} {3 0.0}                                   # station id & istrumnt h.
    {5 2} {7 6.283145} {8 1.120836} {4 PR0} {112 2}  # target id, hz, v, code,
    {5 T1} {7 2.022707} {8 1.542995} {4 RL} {112 2}  # number of faces
    {5 3} {7 3.001701} {8 1.611722} {4 OR} {112 2}
    {5 T2} {7 3.006678} {8 1.550763} {4 ATR1} {112 2}
    {5 4} {7 3.145645} {8 1.610680} {4 PR2} {112 2}
    {5 1} {7 6.002123} {8 1.172376} {4 PR} {112 2}
    {5 9} {7 6.235123} {8 1.178538} {4 RLA} {112 2}

    instead of code=4 you can define prism constant using code=20
    prism constant units are meter

Sample dmp file::

    station; id; hz; v; code;faces
    S2;2;6.283145;1.120836;PR0;2
    S2;T1;2.022707;1.542995;RL;2
    S2;3;3.001701;1.611722;OR;2
    S2;T2;3.006678;1.550763;ATR1;2
    S2;4;3.145645;1.610680;PR2;2
    S2;1;6.002123;1.172376;PR;2

Codes describe target type:

- ATRn: prism and automatic targeting, n referes to prism type 0/1/2/3/4/5/6/7 round/mini/tape/360/user1/user2/user3/360 mini
- ATR-n: prims and automatictargeting but wait for a keypress to measure
- PRn: prism, n referes to prism type 0/1/2/3/4/5/6/7 round/mini/tape/360/user1/user2/user3/360 mini, manual targeting
- RL: refrectorless observation, manual targeting
- RLA: reflectorless observation (automatic)
- OR: do not measure distance (orientation), manual targeting

In case of PR/RL/OR the program stops and the user have to aim at the target

Robotplus
=========

RobotPlus is the most comprehensive application. It is based on FileGen, 
BlindOrientation, FreeStation and Robot applications.
Besides the total station metheorological sensors are also supported.

There are so many parameters to this aplication that a JSON configuration 
file is applied to describe parameters.

The whole process consists of the following steps:

# Load JSON configuration file
# Generate the observations from the input coordinate list (using FileGen)
# Orientate total station (usinf BlindOrientation)
# Make observations to the reference/fix points (using Robot)
# Calculate station coordinates and precise orientation (using FreeStation)
# Make observations to the monitoring points and store data

During the process a log file is written, the log level DEBUG/INFO/WARNING/ERROR/FATAL can be set in the JSON config.

Usage: robotplus.py config.json

- config.json: JSON file describing parameters

There are several parameters in a config file, most parameters are optional.
Parameters:

- log_file: path to log file, file must exist!
- log_level: 10/20/30/40/50 for DEBUG/INFO/WARNING/ERROR/FATAL
- log_format: format string for log (default: "%(asctime)s %(levelname)s:%(message)s"), optional
- station_type: 1100/1200/1800
- station_id: pont id for the station
- station_height: instrument height above point, optional (default: 0)
- station_coo_limit: limitation for station coordinate change from free station (default 0.01 m), optional
- orientation_limit: distance limit for orientation to identify a target (default 0.1 m)
- faces: number of faces to measure (first face left for all pointt then face right) (default 1)
- face_coo_limit: maximum difference for face left and face right coords (m) (default: 0.01 m)
- face_dir_limit: maximum difference for face left and face right angle (rad) (default 0.0029 60")
- face_dist_limit: maximum difference for face left and face right dist (m) (default 0.01 m)
- directfaces: number of faces to measure (face left and right are measured directly) (default 1)
- avg_faces: 1/0 calculate average for faces of monitoring points and store only average/do not calculate average store individual faces, default: 1
- fix_list: list of fix points to calculate station coordinates, optional (default: empty)
- mon_list: list of monitoring points to measure, optional (default: empty)
- max_try: maximum trying to measure a point, optional (default: 3)
- delay_try: delay between tries, optional (default: 0)
- dir_limit: angle limit for false direction in radians (default 0.015. 5')
- dist_limit: distance limit for false direction in meters (default 0.1 m)
- port: serial port to use (e.g. COM1 or /dev/ttyS0 or /dev/ttyUSB0)
- coo_rd: source to get coordinates from
- coo_wr: target to send coordinates to
- obs_wr: target to send observations to
- met_wr: target to send meteorological observations to, optional (default: no output)
- inf_wr: target to send general information to
- decimals: number of decimals in output (coords and distances), optional (default: 4)
- gama_path: path to GNU Gama executable, optional (default: empty, no adjustment)
- stdev_angle: standard deviation of angle measurement (arc seconds), optional (default: 1)
- stdev_dist: additive tag for standard deviation of distance measurement (mm), optional (default: 1)
- stdev_dist1: multiplicative tag for standard deviation of distance measurement (mm), optional (default: 1.5)
- dimension: dimension of stored points (1D/2D/3D), optional (default: 3)
- probability: probability for data snooping, optional (default: 0.95)
- blunders: data snooping on/off 1/0, optional (default: 1)
- met: met sensor name WEBMET/BMP180/SENSEHAT, optional default None
- met_addr: URL to webmet data, optional (default: empty)
- met_par: parameters to webmet service, optional (default: empty)

Sample config file::

	{ "log_file": "/home/siki/ulyxes/data/rp103.log",
	  "log_level": 10,
	  "station_type": "1200",
	  "station_id": "103",
	  "station_height": 0.369,
	  "station_coo_limit": 0.1,
	  "orientation_limit": 0.05,
	  "faces": 1,
	  "directfaces": 1,
	  "fix_list": ["601", "603", "605", "607"],
	  "mon_list": ["602", "604", "606", "608", "601", "603", "605", "607"],
	  "max_try": 3,
	  "delay_try": 0,
	  "dir_limit": 0.015,
	  "port": "/dev/ttyUSB0",
	  "coo_rd": "/home/siki/ulyxes/data/labor.coo",
	  "coo_wr": "/home/siki/ulyxes/data/labor_out.coo",
	  "obs_wr": "/home/siki/ulyxes/data/labor_obs.geo",
	  "met_wr": "",
	  "inf_wr": "/home/siki/ulyxes/data/labor_inf.csv",
	  "decimals": 4,
	  "gama_path": "/home/siki/gama-2.07/bin/gama-local",
	  "stdev_angle": 1,
	  "stdev_dist": 1,
	  "stdev_dist1": 1.5,
	  "dimension": 3,
	  "probability": 0.95,
	  "blunders": 0
	}
