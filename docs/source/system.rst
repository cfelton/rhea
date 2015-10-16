
System
======

The ``rhea`` package provides frameworks for building complex digital
circuits.  These include modular and scalable `interfaces`_ and
`modules`_.  The following describes the specification for the 
frameworks being developed into the `rhea` package.

.. _myhdl : http://www.myhdl.org
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

.. _register : http://

The following is a short example building a simple register file.


.. code-block::python

    from rhea.system import RegisterFile, Register

    # create a register file
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

     The current implementation requires all the register in a
     register file to be the same width.  
     
     
The above example defines a register file to be used.  This can be 
used in a new component/peripheral.  


.. code-block::python

    def led_blinker(glbl, membus, leds):
        clock = glbl.clock
        # instantiate the register interface module and add the
        # register file to the list of memory-spaces
        regfile.base_address = 0x8240
        regfile_inst = membus.add(glbl, regfile)

        # instantiate different LED blinking modules
        led_modules = (led_stroby, led_dance, led_count,)
        led_drivers = [Signal(leds.val) for _ in led_modules]
        mod_inst = []
        for ii, ledmod in enumerate(led_modules):
            mod_inst.append(ledmod(glbl, led_drivers[ii]))

        @always(clock.posedge)
        def beh_led_assign():
            leds.next = led_drivers[regfile.mode]

        return regfile_inst, mod_inst, beh_led_assign


The `led_blinker` module demonstrates how to add the created `regfile` to 
the memory-mapped bus and get myhdl instance that provides the logic 
to read and write the register file from the bus interface passed to the 
module. 

When instantiating the :py:func:`led_blinker` `module`_

.. _module : http://docs.myhdl.org/en/stable/manual/structure.html#structural-modeling


Memory Map Interfaces
---------------------
The :Register File: section examples eluded to the memory-map (or CSR)
interfaces and how they can be connected to register file.  The `rhea`
project contains the following memory-map interfaces:

   * :py:class:`Barebone`
   * :py:class:`Wishbone`
   * :py:class:`AvalonMM`
   * :py:class:`AXI4Lite`

Each of these implement a memory-map bus type/specification and each
can be passed as and interface to a module.

When interfacing to a register file, the register file is added to the
bus as shown in the previous example with the :py:func:`MemoryMapped.add`
function.  The register file covers many use cases for adding control
and status interfaces to different components.  Each interface also
contains a module to adapt the memory-map interface to a *generic*
interface.  In this case each bus is mapped to the :py:class:`Barebone`
bus with the :py:func:`MemoryMapped.map_to_generic` function / `myhdl`_ `module`_.