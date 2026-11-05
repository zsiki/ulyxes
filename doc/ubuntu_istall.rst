Installing pyapi and pyapps on Ubuntu/debian/raspbian Linux
===========================================================

Prerequisites
-------------

During the installation of prerequisites some extra packages will be installed,
too.

Serial test
~~~~~~~~~~~

Optional for testing serial connection to the instrument. With graphical user interface use cutecom.

.. code:: bash

	sudo apt-get install cutecom
	
or with command line use setserial and minicom.

.. code:: bash

	sudo apt-get install setserial
	sudo apt-get install minicom


Python 3.x & pip
~~~~~~~~~~~~~~~~~~

.. code:: bash

	sudo apt-get install python3 python3-pip python3-dev
	 pip install setuptools


PySerial (Serial communication to sensor)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

	pip install pyserial

On Linux the serial ports are protected. The root user and those are in the
dialout group are able to read/write serial ports. To add yourself to the
dialout group use the following command

.. code:: bash

	sudo usermod -a -G dialout $USER

PyBluez (Bluetooth communication to sensor)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash
	
	sudo apt-get install bluetooth libbluetooth-dev
	pip install pybluez

If pip install of pybluez failed with "error in PyBluez setup command: use_2to3 is invalid", try install from sources.

.. code:: bash

	pip install git+https://github.com/pybluez/pybluez.git#egg=pybluez
	
PyYaml (to read camera calibration data)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

	pip install pyyaml

numpy (for camera applications)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

    pip install numpy
	
Matplotlib (to display camera/image ddata)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

	sudo apt install python3-matplotlib

GNU GaMa
~~~~~~~~

Optional used only by robotplus.py, anystation.py and freestation.py.
GNU GaMa is built from sources

.. code:: bash

	sudo apt-get install autoconf automake
	git clone https://git.savannah.gnu.org/git/gama.git
	cd gama
	./autogen.sh
	./configure
	make
	sudo make install

.. note:: Please note that the required autoconf version by GNU GaMa may be
   newer then the installed version. To check installed autoconf version
   use ``autoconf -V`` command.

OpenCV
~~~~~~

Optional used by WebCam class. opencv-contrib-python contains code to 
identify ArUco codes in images which is used by the applications in camera
folder.

.. code:: bash

	sudo apt-get install libopencv-dev 
	pip install opencv-python
	pip install opencv-contrib-python

Wifi
~~~~

Optional used by WifiCollector class.

.. code:: bash

	pip install wifi
	
I2C interface
~~~~~~~~~~~~~

Optional available only on Raspberry Pi.
See http://www.instructables.com/id/Raspberry-Pi-I2C-Python/step2/Enable-I2C/

SpatiaLite/SqLite
~~~~~~~~~~~~~~~~~

Optional used by robotplus if SqLiteWriter selected.

.. code:: .bash

	sudo apt-get install sqlite3
	sudo apt-get install spatialite-bin

Ulyxes
------

Install only the latest version from GitHub:

.. code:: bash

	cd ~
	wget https://github.com/zsiki/ulyxes/zipball/master/ -O ulyxes.zip
	unzip ulyxes.zip

Or make a local copy of the git repository:

.. code::

	cd ~
	git clone https://github.com/zsiki/ulyxes.git

You can move the whole ulyxes install directory to any other place in your 
file system and you can also rename the ulyxes install directory. You had 
better not to change directory and file names under the install directory.

Set PYTHONPATH variable in your .profile to start ulyxes applications from any folder

.. code::

	export PYTHONPATH=$HOME/ulyxes/pyapi:$HOME/ulyxes/camera:$HOME/ulyxes/pyapps
	
