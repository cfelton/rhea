
Note::

   This project is in beta mode and under heavy development.  Not all
   features described in the documentation are implemented.  The features
   described in the documentation are in the process of being implemented.
   Many of the modules, interfaces, and functions may change considerably
   before the first release.


Introduction
=============
The ``rhea`` package is a collection of HDL cores written in `myhdl`_.
The ``rhea`` package is more than just a collection of cores it is also
a framework for creating complex digital circuits.  The ``rhea`` package
includes a complete test suite.

.. _myhdl : http://www.myhdl.org


The ``rhea`` package is divided into the following subpackages:

   - **rhea**: The top-level namespace contains a small number of components
     (thin layer) use to build the subblocks (cores)

   - **system**: The *system* subpackage contains the `interface`_ classes and
     other useful tools to assist in the building of complex digital designs.

   - **models**: This subpackage contains various models used for development
     and verification

   - **cores**: The *cores* subpackage contains the HDL implementation of the
     digital hardware cores.

   - **build**: This subpackage automates various tool-flows (compilation).
     The automation mainly supports FPGA vendor tool-flows.  The
     ``build.boards`` is a collection of board definitions.  The build
     automation is used by selecting a board and automating the build
     for the board.

   - **vendor***: The vendor subpackage is an encapsulation of device
     primitives.

.. _interface: http://docs.myhdl.org/en/stable/whatsnew/0.9.html#interfaces-conversion-of-attribute-accesses

.. toctree::
   :maxdepth: 1

   base_building_blocks
   system/index
   cores/index
   models/index
   build/build
   build/board_definition
   examples/index


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

