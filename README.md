
**NOTE** the following is a work-in-progress (WIP) and has not reached
a minor release point.  If you happen to come across this public repository
feel free to try it out and contribute.  This repository will
be unstable until the first minor release 0.1. 
 
[![Documentation Status](https://readthedocs.org/projects/rhea/badge/?version=latest)](https://readthedocs.org/projects/rhea/?badge=latest) 
[![Build Status](https://travis-ci.org/cfelton/rhea.svg)](https://travis-ci.org/cfelton/rhea) 
[![Join the chat at https://gitter.im/cfelton/rhea](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/cfelton/rhea?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

<!-- banner -->
 
rhea 
====

The rhea python package is a collection of HDL cores written 
in MyHDL.  The myhdl package can be retrieved from http://www.myhdl.org


the name
--------
Pronounced ray (as in ray-gun), just a random name and not 
pronoucned the same as the bird or moon.
 
 
dependencies
------------
   - [myhdl](www.myhdl.org) 0.9 or later
   - [pytest](www.pytest.org) for the test suite
   
   
quick start
-----------
If you are not familiar with [myhdl](www.myhdl.org) starting with the
[myhdl manual]() and [examples]() is recommended.  General myhdl questions 
can be answered on the [#myhdl IRC channel]() or on the [myhdl mailing-list]().  
I am often available to answer `rhea` specific questions on the previously
mentioned communications or the `rhea` gitter can be used.


general comments
----------------
**IMPORTANT NOTE** this repository is under development and is using
features from a development version of MyHDL (1.0dev).  If you 
wish to try out this package get 
[the development myhdl](https://github.com/jandecaluwe/myhdl)  (you will 
need to clone it and install the source).  The first 
*rhea* release will not occur until myhdl 1.o is released (probably much
later).

This code/package is licensed under the ~~LGPL~~ ??? license.  This allows 
anyone to use the package in their projects with no limitations ~~but
if the code in the `rhea` package is modified those modifications need to
be made available to the public (not the code the cores are used 
in or with).~~  Questions and other license options email me.

The following are the definition of some terms used in this README :


   * cores : the building blocks of a system.  Also, know as IP
     (intellectual property).

   * system : the digital design being implement, synonymous with 
     system-on-a-chip, not using the term system-on-a-chip (SoC) 
     because SoC it is typically reserved for systems that contains 
     a CPU.  In this document and the example the **system** can be
     a SoC or other complex digital design.

   * register : collection of bits that retain state. 

   * register file : collection of same-sized registers, a register
     file is organized into read-write entities and read-only entities.
     A register-file is a programming/configuration interface to a 
     core.

   * CSR: control and status registers also known as config and status.  
     This term is commonly used for the memory-mapped interface to the cores.


getting started
-------------------
To get started with the latest version (repo version) checkout out the
code and run setup in *develop* mode.

Dependencies:
  * myhdl
  * py.test
  * gizflo (optional)


Install the latest myhdl.

```
  # get the required python packages, myhdl, gizflo,
  # and the latest minnesota package.
  >> git clone https://github.com/jandecaluwe/myhdl
  >> sudo python setup.py install
  >> cd ..
```

or

```
  >> pip install git+https://github.com/jandecaluwe/myhdl
```

See www.myhdl.org for information on myhdl, the *mn* package
requires a 0.9 feature -interfaces-.  After 0.9 is release the
official myhdl releases should be used.  Refer to the myhdl
mailing-list for more information.


Install the FPGA build package (optional only needed to build
the example bitstreams).

```
  # FPGA build and misc HDL tools
  >> git clone https://github.com/cfelton/gizflo
  >> cd gizflo
  >> sudo python setup.py install 
  >> cd ..
```

After the dependencies have been installed clone this repository
to get started.

```
  >> git clone https://github.com/cfelton/minnesota
  >> cd minnesota
  # requires setuptools
  >> python setup.py develop
```

The tests can be run from the test directory.

```
  # attempt to run the tests
  >> cd test
  >> py.test
```

If the `gizflo` package was installed and the FPGA vendor tools
are installed attempt to build one of the example projects.

```
  # try to compile one of the examples 
  # (requires FPGA tools installed and gizflo)
  >> cd ../examples/boards/nexys/fpgalink
  >> python test_fpgalink.py
  >> python compile_fpgalink.py
```


test
----
The test directory contains test for the different cores in the package.

Run the tests in the test directory:
```
>> cd test
>> py.test
```

Run the tests in the examples directory:
```
>> cd examples
>> py.test
```


examples
--------
In the examples directory are projects that demonstrate how to build 
systems using the cores and various tools and target a particular FPGA 
development board.  As mentioned above the examples have an additional 
dependency, [gizflo]() to create the actual bitstreams.  

