
Note, the ``rhea`` package is under development, a first minor
release (0.1) has not been made.  Significant changes and design 
decision are occurring.  Some of the information in these documents
is documentation on non-existing features, features that are
currently being implemented but not completed.


##############
Introduction
##############

The ``rhea`` package is a collection of HDL cores written in
`myhdl`_.  The ``rhea`` package is more than just a collection 
of cores it is also a framework for creating complex digital
circuits.  The ``rhea`` package also includes a complete test
suite.

.. _myhdl : http://www.myhdl.org

The ``rhea`` package is divided into the following subpackages:

   * system
   * models
   * cores
   * build 
   * vendor


System
======
The system subpackage contains the [interfaces]() and other
useful tools to assist in building complex digital designs.

.. add link to ControlAndStatus, MemoryMapped, Streaming ... 


Models
======
This subpackage contains various models used for development
and verification.

.. To facilitate development and verification models are created 
.. of external devices or "golden" models of an internal peripheral 
.. or processing block.


Cores
=====
This subpackage contains the core implementations.


Build
=====
This subpackage automates various tool-flows (compilation).  
The automation mainly supports FPGA vendor tool-flows.  The 
``build.boards`` is a collection of board definitions.  The
build automation is used by selecting a board and automating
the FPGA build for that board.


Vendor 
======
The vendor subpackage is an encapsulation of device primitives
 for various vendors (e.g. Altera, Xilinx, Lattice, etc.).










