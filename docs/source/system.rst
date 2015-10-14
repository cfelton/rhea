
System
======

The ``rhea`` package provides frameworks for building complex digital
circuits.  These include modular and scalable `interfaces`_ and
`modules`_.  The following describes the specification for the 
frameworks being developed into the `rhea` package.

.. _modules : http://docs.myhdl.org/en/stable/manual/structure.html#structural-modeling
.. _interfaces : http://docs.myhdl.org/en/stable/whatsnew/0.9.html#interfaces-conversion-of-attribute-accesses


Register Files
--------------
When creating components for a design often a register file is included
The register file is used for the control and status access (CSR) of
the component.
A regiter file is simply a collection of `registers`_ that are used to
control the component and read status. The register file is accessed by 
a memory-mapped bus.  The register file provides dynamic control and
status of the component.

The objects to create a register file encapsulate much of the detail 
required for typical register-file definition.  In addition provides 
a mechanism for static definition (no bus present).

.. _register :

The following is a short example building a simple register file.

.. code-block::python

    from rhea.system import RegisterFile, Register

    # create a registrer file
    regfile = RegisterFile()

    # create a status register and add it to the register file
    reg = Register('status', width=8, access='ro', default=0)
    regfile.add_register(reg)

    # create a control register with named bits and add
    reg = Register('control', width=8, access='rw', default=1)
    reg.add_named_bits('enable', bits=0, comment="enable the compoent")
    reg.add_named_bits('pause', bits=1, comment="pause current operation")
    reg.add_named_bits('mode', bits=(4,2), comment="select mode")
    regfile.add_register(reg)
    
    
.. Note::

     The current implrementation requires all the register in a 
     register file to be the same width.  
     
     
The above example defines a register file to be used.  This can be 
used in a new component/peripheral.  

.. code-block::python

   def led_blinker(glbl, membus, leds):
       
       # instantiate the module to interface to the the regfile
       
       # instantiate different LED blinking modules
       led_modules = (led_stroby, led_dance, led_count,)
       mleds = [Signal(leds.val) for _ in led_modules]
       mods = []
       for ii, ledmod in enumerate(led_modules): 
           mods += ledmod(glbl, mleds[ii])
       
       # 
