
##############
Introduction
##############

The ``rhea`` package is a collection of HDL cores written in
`myhdl`_.  The ``rhea`` package is more than just a collection of
cores it is also a framework for creating complex digital
circuits.  The ``rhea`` package includes a complete test
suite.

.. _myhdl : http://www.myhdl.org

The ``rhea`` package is divided into three main subpackages:

   * system
   * models
   * cores


System
======
The system subpackage contains the [interfaces]() and other
useful tools to assist in building complex digital designs.

regfile
-------
The register file objects provide simple methods to define
registers and collections of registers.  The registers files
can be easily be connected to memory-mapped bus (e.g
wishbone, avalon, etc.).

Defining a Register File
^^^^^^^^^^^^^^^^^^^^^^^^
The following is a example defining a couple registers:

.. code-block::python

    regfile = RegisterFile(width=8)
    reg0 = Register('status', 0x0020, 8, 'ro', 0)
    regfile.add_register(reg0)
    reg1 = Register('control', 0x0024, 8, 'rw', 0)
    regfile.add_register(reg1)

.. regfile needs to be enhanced to automatically determine
.. the best list-of-signal organization.  The register definitions
.. should be able to be defined logically and randomly and the
.. RegisterFile will organize the list-of-signals as needed ...
.. Future enhancement that can occur under the hood


Models
======
This subpackage contains various models used for development
and verification.

.. To facilitate development and verification models are created of external
.. devices or "golden" models of an internal peripheral or processing block.


Cores
=====
This subpackage contains the core implementations.








