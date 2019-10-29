Installing pyapi and pyapps on Ubuntu/debian/raspbian Linux
===========================================================

Prerequisites
-------------

During the installation of prerequisites some extra packages will be installed,
too.

Serial test
~~~~~~~~~~~

Optional for testing serial connection to the instrument.

.. code:: bash

	sudo apt-get install cutecom

Python 3.x & pip
~~~~~~~~~~~~~~~~~~

.. code:: bash

	sudo apt-get install python3 python3-pip python3-dev
	sudo pip3 install setuptools

.. note::
	Ulyxes is Python 2 compatible. Please install the correspondent Python 2 libraries in that case.

PySerial (Serial communication to sensor)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

	sudo pip3 install pyserial

On Linux the serial ports are protected. The root user and those are in the
dialout group are able to read/write serial ports. To add yourself to the
dialout group use the following command

.. code:: bash

	sudo usermod -a -G dialout YOUR_USER_NAME

PyBluez (Bleutooth communication to sensor)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash
	
	sudo apt-get install bluetooth libbluetooth-dev
	sudo pip3 install pybluez


GNU GaMa
~~~~~~~~

Optional used only by robotplus.py
GNU GaMa is built from sources

.. code:: bash

	sudo apt-get install autoconf automake
	git clone https://git.savannah.gnu.org/git/gama.git
	cd gama
	./autogen.sh
	./configure
	make
	sudo make install

OpenCV
~~~~~~

Optional used by WebCam class.

.. code:: bash

	sudo apt-get install libopencv-dev 
	sudo pip3 install opencv-python
	
Wifi
~~~~

Optional used by WifiCollector class.

.. code:: bash

	sudo pip3 install wifi
	
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
