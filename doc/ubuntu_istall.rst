Installing pyapi and pyapps on Ubuntu Linux
===========================================

Prerequisites
-------------

During the installation of prerequisites some extra packages will be installed,
too.

Serial test
~~~~~~~~~~~

Optional for testing serial connection to the instrument.

.. code:: bash

	sudo apt-get install cutecom

Python 2.7.x & pip
~~~~~~~~~~~~~~~~~~

.. code:: bash

	sudo apt-get install python python-pip

PySerial
~~~~~~~~

.. code:: bash

	sudo pip install pyserial

On Linux the serial ports are protected. The root user and those are in the
dialout group are able to read/write serial ports. To add yourself to the
dialout group use the following command

.. code:: bash

	sudo usermode -a -G dialout YOUR_USER_NAME

GNU GaMa
~~~~~~~~

Optional used only by robotplus.py
GNU GaMa is built from sources

.. code:: bash

	git clone git:/git.sv.gnu.org/gama.git
	cd gama
	./autogen.sh
	./configure
	make
	sudo make install

OpenCV
~~~~~~

Optional used by WebCam class.

.. code:: bash

	sudo apt-get install libopencv-dev python-opencv
	
Wifi
~~~~

Optional used by WifiCollector class.

.. code:: bash

	sudo pip install wifi
	
I2C interface
~~~~~~~~~~~~~

Optional available only on Raspberry Pi.
See http://www.instructables.com/id/Raspberry-Pi-I2C-Python/step2/Enable-I2C/

Qt4
~~~

Optional, used by robotplus.py

.. code:: bash

	sudo apt-get install libqtcore4 python-qt4

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

Make a local copy of the git repository:

.. code::

	cd ~
	git clone https://github.com/zsiki/ulyxes.git

You can move the whole ulyxes install directory to any other place inyour file system and you can also rename the ulyxes install directory. You had better not to change directory and file names under the install directory.
