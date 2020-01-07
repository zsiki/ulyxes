Ulyxes PyAPI developer's documentation
**************************************

.. toctree::
    :maxdepth: 2

Ulyxes PyAPI provides several classes to handle surveyor's sensors e.g. totalstations, NMEA GNSS receivers, etc.

GENERIC MODULES
===============

Angles
::::::

.. automodule:: angle
   :members:

Reader
::::::

.. automodule:: reader
   :members:

File Reader
:::::::::::

.. automodule:: filereader
   :members:

Csv Reader
::::::::::

.. automodule:: csvreader
   :members:

Geo Reader
:::::::::::

.. automodule:: georeader
   :members:

HTTP Reader
:::::::::::

.. automodule:: httpreader
   :members:

JSON Reader
:::::::::::

.. automodule:: jsonreader
   :members:

Configuration Reader
::::::::::::::::::::

.. automodule:: confreader
   :members:

SqLite Reader
:::::::::::::

.. automodule:: sqlitereader
   :members:

INTERFACES
==========

Interfaces handle the connection to the physical sensors.

Generic Iface
:::::::::::::

.. automodule:: iface
   :members:

Local Iface
:::::::::::

.. automodule:: localiface
   :members:

Serial Iface
::::::::::::

.. automodule:: serialiface
   :members:

Bluetoth Iface
::::::::::::::

.. automodule:: bluetoothiface
   :members:

Video Iface
:::::::::::

.. automodule:: videoiface
   :members:

I2C Iface
:::::::::

.. automodule:: i2ciface
   :members:

WEB Iface
:::::::::

.. automodule:: webiface
   :members:

Gama Iface
::::::::::

.. automodule:: gamaiface
   :members:

MEASURE UNITS
=============

Measure units are responsible for the specific instrument features.

Generic Measure Unit
::::::::::::::::::::

.. automodule:: measureunit
   :members:

Leica Measure Unit
::::::::::::::::::

.. automodule:: leicameasureunit
   :members:

Leica TCA 1800 Unit
:::::::::::::::::::

.. automodule:: leicatca1800
   :members:

Leica TPS 1200 Unit
:::::::::::::::::::

.. automodule:: leicatps1200
   :members:

Leica TCRA 1100 Unit
::::::::::::::::::::

.. automodule:: leicatcra1100
   :members:

Trimble 5500 Unit
:::::::::::::::::

.. automodule:: trimble5500
   :members:

Leica DNA Unit
::::::::::::::

.. automodule:: leicadnaunit
   :members:

NMEA GNSS Unit
::::::::::::::

.. automodule:: nmeagnssunit
   :members:

Video Unit
::::::::::

.. automodule:: videomeasureunit
   :members:

BMP180 Unit
:::::::::::

.. automodule:: bmp180measureunit
   :members:

Wifi Unit
:::::::::

.. automodule:: wifiunit
   :members:

Web Met Unit
::::::::::::

.. automodule:: webmetmeasureunit
   :members:

SENSORS/INSTRUMENTS
===================

Sensors or instruments integrate the interface, the measure unit and an
optional writer. Interface is responsible for the communication with the
physical device, measure unit gives the specific features of intruments,
the writer adds the storing logic to observed data.

Generic Instrument
::::::::::::::::::

.. automodule:: instrument
   :members:

Totalstation
::::::::::::

.. automodule:: totalstation
   :members:

GNSS
::::

.. automodule:: gnss
   :members:

Digital Level
:::::::::::::

.. automodule:: digitallevel
   :members:

Web Camera
::::::::::

.. automodule:: webcam
   :members:

BMP180 Air Pressure Sensor
::::::::::::::::::::::::::

.. automodule:: bmp180
   :members:

WiFi Collector
::::::::::::::

.. automodule:: wificollector
   :members:

Web Met Sensor
::::::::::::::

.. automodule:: webmet
   :members:

WRITERS
=======

Writers are responsible to store observed data on different media.

Writer
::::::::::::::

.. automodule:: writer
   :members:

Echo Writer
:::::::::::

.. automodule:: echowriter
   :members:

File Writer
:::::::::::

.. automodule:: filewriter
   :members:

CSV Writer
::::::::::

.. automodule:: csvwriter
   :members:

Image Writer
::::::::::::

.. automodule:: imagewriter
   :members:

HTTP Writer
:::::::::::

.. automodule:: httpwriter
   :members:

Geo Writer
::::::::::

.. automodule:: geowriter
   :members:

SqLite Writer
:::::::::::::

.. automodule:: sqlitewriter

SAMPLE APPLICATIONS
===================

Measure to Prism
::::::::::::::::

.. automodule:: measuretoprism
   :members:

NMEA Demo
:::::::::

.. automodule:: nmea_demo
   :members:

Measure matrix
::::::::::::::

.. automodule:: measurematrix
   :members:

Horizontal section
::::::::::::::::::

.. automodule:: horizsection
   :members:

Section
:::::::

.. automodule:: section
   :members:

Filemaker
:::::::::

.. automodule:: filemaker
   :members:

Filegen
:::::::

.. automodule:: filegen
   :members:

Blind orientation
:::::::::::::::::

.. automodule:: blindorientation
   :members:

Freestation
:::::::::::

.. automodule:: freestation
   :members:

Robot
:::::

.. automodule:: robot
   :members:

Robot+
::::::

.. automodule:: robotplus
   :members:

Coords
::::::

.. automodule:: coords
   :members:

