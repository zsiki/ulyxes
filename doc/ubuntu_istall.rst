Installing pyapi and pyapps on Ubuntu Linux
===========================================

Prerequisites
-------------

Python 2.7.x & pip
~~~~~~~~~~~~~~~~~~

.. code:: bash

	sudo apt-get install python python-pip

PySerial
~~~~~~~~

.. code:: bash

	sudo pip install pyserial

GNU GaMa
~~~~~~~~

Optional used only by robotplus.py

.. code:: bash

	git clone git:/git.sv.gnu.org/gama.git
	cd gama
	./autogen.sh
	./configure
	make
	sudo make install

Ulyxes
~~~~~~

.. code:: bash

	cd ~
	git clone https://github.com/zsiki/ulyxes.git

