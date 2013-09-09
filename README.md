minnesota
=========

A collection of HDL cores written in MyHDL.  The "mn" package is 
dependent on the myhdl package.  The myhdl package can be retrieved
from http://www.myhdl.org.

This repo is a mirror, more stable releases are sync'd on github.
Feel free to pull-request to this repo.  The more active developed
version can be accessed here: https://bitbucket.org/cfelton/minnesota

The examples have an additional dependency, the myhdl_tools package.
This package is used to manage different development boards and to 
simplify the FPGA tool flow.  See the examples for directory for 
FPGA compile templates for different boards.  The current version 
of the myhdl_tools compile scripts only support Xilinx tool flow
(others soon to follow).

fpgalink
---------
This is a MyHDL implementation of the HDL for the *fpgalink*
project.  The fpgalink HDL core can be instantiated into 
a design:


    from mn.cores.usb_ext import fpgalink_fx2
    from mn.cores.usb_ext import fl_fx2
 
    # ...
    # fpgalink interface 
    g_fli = fpgalink_fx2(clock,reset,fx2_bus,fl_bus) 

    # ...

For simulation and verification the *fpgalink* interface can
stimulated using the FX2 model and high-level access functions:


    from mn.cores.usb.ext import fpgalink_fx2
    from mn.cores.usb_ext import fpgalink_host
    from mn.cores.usb_ext import fl_fx2 
 
    # instantiate the components, etc. (see examples in example dir)
    # ...
    
    # high-level access to the digital (FPGA) design
    fh.WriteAddress(1, [0xC3])     # write 0xCE to address 1
    fh.WriteAddress(0, [1,2,3,4])  # write 1,2,3,4 to address 0
    rb = fh.ReadAddress(1)         # read address 1

fifo ramp
----------
This is a simple module that will create a ramp and interface to a FIFO,
(fill the FIFO while not full).  This is used for system/lab testing.  A
ramp is generated and a received ramp can be verified (e.g. generate a
ramp in the FPGA and verify ramp recieved on host PC over usb).

spi
---
This is a simple SPI port that.  This SPI port parameters are configured at
design time and not run time.




