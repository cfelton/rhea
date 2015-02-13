**NOTE** the following is a work-in-progress (WIP) and has not reached
a minor release point.  If you happen to come across this public repository
feel free to try it out and contribute if you want.  This repository will
be unstable until the first minor release 0.1. 
 
minnesota
=========

The minnesota python package is a collection of HDL cores written 
in MyHDL.  The "mn" package is dependent on the myhdl package (obviously).  
The myhdl package can be retrieved from http://www.myhdl.org

The examples have an additional dependency, the myhdl_tools package.
This package is used to manage different development boards and to 
simplify the FPGA tool flow.  See the examples directory for FPGA 
compile templates for various boards.  

**IMPORTANT NOTE** this repository is under development and is using
features from a development version of MyHDL (0.9dev).  An older version 
with a usable *fpgalink* core can be found on 
[github](https://github.com/cfelton/minnesota) .  If you 
wish to try out this package get a 
[the development myhdl](http://bitbucket.org/jandecaluwe/myhdl)  
(will need to clone it and install the source).  The first 
*mn* release will not occur until myhdl 0.9 is released.


This code/package is licensed user the LGPL license.  This allows 
anyone to use the package in their projects with no limitations but
if the code in the mn package is modified those modifications need to
be made available to the public.  Questions and other license options
email me.


The following are the definition of some terms used in this README :


   * cores : the building blocks of a system.  Also, know as IP
     (intellectual property).

   * system : the digital design being implement, synonymous with 
     system-on-a-chip, not using the term system-on-a-chip (SoC) 
     because SoC it is typically reserved for systems that contains 
     a CPU.  In this document and the example the **system** can be
     a SoC or other complex digital design

   * register : collection of bits that retain state 

   * register file : collection of same-sized registers, a register
     file is organized into read-write entities and read-only entities.
     A register-file is a programming/configuration interface to a 
     core.


getting started
-------------------
To get started with the latest version (repo version) checkout out the
code from bitbucket and run setup in *develop* mode.
 

```
  # get the required python packages, myhdl, myhdl_tools,
  # and the latest minnesota package.
  >> hg clone https://bitbucket.org/jandecaluwe/myhdl
  >> cd myhdl
  >> hg up -C 0.9-dev
  >> sudo python setup.py install
  >> ..
  # see www.myhdl.org for information on myhdl, the *mn* package 
  # requires a 0.9 feature-interfaces-.  After 0.9 is release the
  # official myhdl releases should be used.  Refer to the myhdl-mailing
  # list for more information.

  # FPGA build and misc HDL tools
  >> hg clone https://bitbucket.org/cfelton/myhdl_tools
  >> cd myhdl_tools
  >> sudo python setup.py install 
  >> cd ..

  >> hg clone https://bitbucket.org/cfelton/minnesota
  >> cd minnesota
  >> python setup.py develop
  # verify the tests run (if not, post a comment)
  >> cd test
  >> py.test
  # try to compile one of the examples 
  # (requires FPGA tools installed)
  >> cd ../examples/nexys/fpgalink
  >> python test_fpgalink.py
  >> python compile_fpgalink.py
```


system (Infrastructure)
-----------------------

In the "mn" package there sub-packages that are not cores or example
systems but tools to build systems.


### regfile
The register file objects provide simple methods to define registers
via Python dicts or Register objects.  From these definitions the 
registers in a peripheral are created and connected to a memory-mapped
bus (e.g. wishbone, avalon, etc). 


#### Defining a Register File


#### Adding a Register File to a Peripheral


#### Adding a Memory-Mapped Bus to a System


### memmap
The memory-map type buses

   * Wishbone
   * Avalon
   * simple



models
------
To facilitate development and verification models are created of external 
devices or "golden" models of an internal peripheral or processing block.



cores
-----
The following is a list of currently implemented cores.


### fpgalink

This is a MyHDL implementation of the HDL for the *fpgalink*
project.  The fpgalink HDL core can be instantiated into 
a design:


```python

    from mn.cores.usbext import m_fpgalink_fx2
 
    # ...
    # fpgalink interface 
    g_fli = m_fpgalink_fx2(clock,reset,fx2bus,flbus) 

    # ...
```

For simulation and verification the *fpgalink* interface can be
stimulated using the FX2 model and high-level access functions:

```python
   from mn.models.usbext import fpgalink_host
   from mn.cores.usbext import fpgalink 
   from mn.cores.usbext import m_fpgalink_fx2
 
   # instantiate the components, etc (see examples in example dir)
   # ...
   # use high-level accessors to 
   fh.WriteAddress(1, [0xC3])     # write 0xCE to address 1
   fh.WriteAddress(0, [1,2,3,4])  # write 1,2,3,4 to address 0
   rb = fh.ReadAddress(1)         # read address 1
```

The following is a pictorial of the verification environment .


For more information on the [fpgalink]() software, firmware, and
general design information see [makestuff]().



### usbp

USB Peripheral, this is another Cypress FX2 controller interface, 
this has two interfaces a "control" interface and a "streaming" 
interface.  This FX2 interface is intended to work with the 
[fx2 firmware]() that configures the controller as a USB CDC/ACM
device (virtual serial port).  The [fx2 firmware]() also has a
couple vendor unique commands that can be sent using the pyusb
(or other low-level USB interfaces like libusb).  The Python
version of the host software (including firmware) can be retrieved
via pip.

|   >> pip install usbp
|   >>> import usbp
|   >>> import serial

One of the tricky items with USB devices is setting the permissions
correctly.  On a linux system to set the …


### fifo ramp


### spi

test
----
The test directory contains test for the different cores in the package.
Most of the test have the additional dependency of the `myhdl_tools`_ 
package.


examples
--------
In the examples directory are projects that demonstrate how to build 
systems using the cores and various tools and target a particular FPGA 
development board.  As mentioned above the examples have an additional 
dependency, `myhdl_tools`_ to create the actual bitstreams.  


### Xess Xula(2)
Examples

   * binary hello


### Digilent Nexys
Examples 

   * binary hello
   * fpgalink
   * usbp


### Open-Source UFO-400
Examples

   * binary hello
   * usbp


### DSPtronics Signa-X1 (sx1)
Examples

   * binary hello
   * fpgalink
   * usbp
   * audio examples
      * audio echo
      * audio streaming