
**NOTE** the following is a work-in-progress (WIP) and has not reached
a minor release point.  If you happen to come across this public repository
feel free to try it out and contribute.  This repository will
be unstable until the first minor release 0.1.  This repository is 
a merge of the `mn` and `gizflo` projects.

<!-- badges -->

[![Documentation Status](https://readthedocs.org/projects/rhearay/badge/?version=latest)](http://rhearay.readthedocs.org/en/latest/) 
[![Build Status](https://travis-ci.org/cfelton/rhea.svg?branch=master)](https://travis-ci.org/cfelton/rhea)
[![Join the chat at https://gitter.im/cfelton/rhea](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/cfelton/rhea?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)


<!-- banner -->
 
 
rhea 
====

The `rhea` python package is a collection of HDL cores written 
in MyHDL.  The myhdl package can be retrieved from http://www.myhdl.org


the name
--------
Pronounced ray (as in ray-gun), just a random name and not 
pronounced the same as the bird or moon.
 
 
dependencies
------------
   - [myhdl](http://www.myhdl.org) 1.0 or later
   - [pytest](http://www.pytest.org) for the test suite
   - [Pillow](https://pillow.readthedocs.org/en/3.0.x/) some video tests utilize the imaging library
   - FPGA vendor tools, only for automated build tools.
   
   
resources
---------
If you are not familiar with [myhdl](http://www.myhdl.org) starting with the
[myhdl manual](http://docs.myhdl.org/en/stable/) and 
[examples](http://www.myhdl.org/examples/) is recommended.  General myhdl 
questions 
can be answered on the [#myhdl IRC channel](https://webchat.freenode.net) 
or on the [myhdl mailing-list](http://dir.gmane.org/gmane.comp.python.myhdl).  
I am often available to answer `rhea` specific questions on the previously
mentioned communications or the `rhea` gitter can be used.


general comments
----------------
**IMPORTANT NOTE** this repository is under development and is using
features from a development version of MyHDL (1.0dev).  If you 
wish to try out this package get 
[the development myhdl](https://github.com/jandecaluwe/myhdl)  (you will 
need to clone it and install the source).  The first 
*rhea* release will not occur until myhdl 1.0 is released (probably much
later).

This code/package is licensed under the MIT license.  This allows 
anyone to use the package in their projects with no limitations.  
Questions and other license options email me.

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
code and run setup in *develop* mode.  The dependencies listed above 
need to be installed.

Install the latest myhdl.

```
  >> git clone https://github.com/jandecaluwe/myhdl
  >> sudo python setup.py install
  >> cd ..
```

or

```
  >> pip install git+https://github.com/jandecaluwe/myhdl
```


After the dependencies have been installed clone this repository
to get started.

```
  >> git clone https://github.com/cfelton/rhea
  >> cd rhea
  # requires setuptools
  >> python setup.py develop
```


### running tests

The tests can be run from the test directory.

```
  # attempt to run the tests
  >> cd test
  >> make test
  # >> py.test
```

**Note** currently an issue exists where the py.test takes an 
extremely long time (more time than it should).  The py.test
test runner is currently not used. 

### generating bitstreams

If the FPGA vendor tools (Xilinx or Altera) are installed the
build examples can be run to generate bitstreams.

```
  # try to compile one of the examples 
  # (requires FPGA tools installed)
  >> cd ../examples/build/
  >> python ex_xula.py
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
In the example directory are projects that demonstrate how to build 
systems using the cores and various tools and target a particular FPGA 
development board.  The [examples/build](https://github.com/cfelton/rhea/examples/build)
contains LED blinky examples for many different boards. 

