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

FileReader
::::::::::

.. automodule:: filereader
   :members:

CsvReader
::::::::::

.. automodule:: csvreader
   :members:

INTERFACES
==========

Interfaces handle the connection to the physical sensor.

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

Video Iface
:::::::::::

.. automodule:: videoiface
   :members:

I2C Iface
:::::::::

.. automodule:: i2ciface
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

WRITERS
=======

Writers are responsible to store observed data on different media.

Generic Writer
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

