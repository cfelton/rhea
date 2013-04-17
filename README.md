minnesota
=========

A collection of HDL cores written in MyHDL.

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
 
    # instatiate teh components, etc (see examples in example dir)
    fh.WriteAddress(1, [0xC3])     # write 0xCE to address 1
    fh.WriteAddress(0, [1,2,3,4])  # write 1,2,3,4 to address 0
    rb = fh.ReadAddress(1)         # read address 1



