
fpgalink
--------

This is a MyHDL implementation of the HDL for the *fpgalink*
project.  The fpgalink HDL core can be instantiated into
a design:

.. code-block::python

    from rhea.cores.usbext import m_fpgalink_fx2

    # ...
    # fpgalink interface
    g_fli = m_fpgalink_fx2(clock,reset,fx2bus,flbus)

    # ...

For simulation and verification the *fpgalink* interface can be
stimulated using the FX2 model and high-level access functions:

.. code-block::python

   from rhea.models.usbext import fpgalink_host
   from rhea.cores.usbext import fpgalink
   from rhea.cores.usbext import m_fpgalink_fx2

   # instantiate the components, etc (see examples in example dir)
   # ...
   # use high-level accessors to
   fh.WriteAddress(1, [0xC3])     # write 0xCE to address 1
   fh.WriteAddress(0, [1,2,3,4])  # write 1,2,3,4 to address 0
   rb = fh.ReadAddress(1)         # read address 1


The following is a pictorial of the verification environment .


For more information on the [fpgalink]() software, firmware, and
general design information see [makestuff]().


usbp
----

USB Peripheral, this is another Cypress FX2 controller interface,
this has two interfaces a "control" interface and a "streaming"
interface.  This FX2 interface is intended to work with the
[fx2 firmware]() that configures the controller as a USB CDC/ACM
device (virtual serial port).  The [fx2 firmware]() also has a
couple vendor unique commands that can be sent using the pyusb
(or other low-level USB interfaces like libusb).  The Python
version of the host software (including firmware) can be retrieved
via pip ::

    >> pip install usbp
    >>> import usbp
    >>> import serial

One of the tricky items with USB devices is setting the permissions
correctly.  On a linux system to set the …
