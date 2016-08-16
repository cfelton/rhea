
System overview
===============

The ``rhea`` package provides frameworks for building complex digital
circuits.  These include modular and scalable `interfaces`_ and
`blocks`_.  The following describes the specification for the
frameworks being developed in the ``rhea`` package.

.. _myhdl : http://www.myhdl.org
.. _blocks : http://docs.myhdl.org/en/stable/manual/structure.html#structural-modeling
.. _interfaces : http://docs.myhdl.org/en/stable/whatsnew/0.9.html#interfaces-conversion-of-attribute-accesses


Control and status 
------------------
One of the goals of the ``rhea`` package is to simplify the assembly 
of systems.  In a complex digital system majority of the blocks will 
have two interfaces.  One being the streaming data in and out of the 
module and the other a control and status interface.  The control 
and status provides a lower-bandwidth interface into the component
(block).

Defining a peripheral specific control-status object (CSO). 

.. code-block:: python

    import rhea.system import ControlStatusBase
    
    # define the control and status signals for a peripheral 
    class ControlStatus(ControlStatusBase):
        modes = enum("counting", "walking", "strobing")
        def __init__(self)
            self.enable = Signal(bool(0))
            self.pause = Signal(bool(0))
            self.mode = Signal(self.modes.counting)
        
        
In a peripheral either the default (defined) control-status object 
CSO can be used and added to the control-status interface.


.. code-block:: python

    @myhdl.block
    def led_blinker(glbl, led, cso):
        # the cso interface provides the control and status for
        # this module
        assert isinstance(ControlStatus)
        clock, reset = glbl.clock, glbl.reset
        modes = ControlStatus.modes
        enabled = Signal(bool(0))

        @always_comb
        def beh_enabled():
            enabled.next = glbl.enable and cso.enable

        @always_seq(clock.posedge, reset=reset)
        def beh_blink():
            if enabled and not cso.pause:
                nextled = 0
                if cso.mode == modes.counting:
                    # counting logic
                elif cso.mode == modes.walking:
                    # walking logic
                elif cso.mode == modes.strobing
                    # strobing logic

                led.next = nextled

        return beh_enable, beh_blink

    led_blinker.cso = ControlStatus


The non-global control and status, i.e. the module specific
control-status is accessed via the ``cso``.  This provides
a clean encapsulation to the block (module).  The ``cso`` can
also include transactors to assist testing and verification.

Creating control status objects
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The above example shows how a collections of control and status signals
are defined in a class.  To help guide the the tools, some additional
information can be defined:

   * ``driven``: set the signal driven attribute to true to indicate a
     read-only (status) attribute.
   * Use the hardware-types :class:`Bit` and :class:`Byte` to
     help drive the how the attributes are organized in a register-file.
     The :class:`Bit` and :class:`Byte` are only used to give
     hints to the register-file builder, if memory-mapped access
     is secondary use the standard :myhdl:class:`Signal`.
   * Use ``initial_value`` property to overwrite the signals initial
     value, this is useful is static configurations.


Register files
--------------
When creating components for a design often a register file is included
The register file is used for the control and status access (CSR) of
the component.
A register file is simply a collection of `registers`_ that are used to
control the component and read status. The register file is accessed by 
a memory-mapped bus.  The register file provides dynamic control and
status of the component.

The objects to create a register file encapsulate much of the detail 
required for typical register-file definition.  In addition provides 
a mechanism for static definition (no bus present).

.. _register : http://

The following is a short example building a simple register file.
Note the following is the manaul method to the example being used
in this document.  Utilizing the :class:`ControlStatusBase` is an
automated process, in majority of the cases register-files should
not be explicitly defined but rather build from a CSO.


.. code-block:: python

    from rhea.system import RegisterFile, Register

    # create a register file
    regfile = RegisterFile()

    # create a status register and add it to the register file
    reg = Register('status', width=8, access='ro', default=0)
    regfile.add_register(reg)

    # create a control register with named bits and add
    reg = Register('control', width=8, access='rw', default=1)
    reg.add_named_bits('enable', bits=0, comment="enable the component")
    reg.add_named_bits('pause', bits=1, comment="pause current operation")
    reg.add_named_bits('mode', bits=(4, 2), comment="select mode")
    regfile.add_register(reg)
    
    
.. Note::

     The current implementation requires all the register in a
     register file to be the same width.  
     
     
The above example defines a register file to be used.  This can be 
used in a new component/peripheral.  


.. code-block:: python

    @myhdl.block
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


The :func:`led_blinker` module demonstrates how to add the created
:class:`RegisterFile` to
the memory-mapped bus and get a myhdl instance that provides the logic
to read and write the register file from the bus interface passed to the 
module. 

.. what was I going to say in this next sentence?
.. When instantiating the :py:func:`led_blinker` `module`_

Note, in the above example a ``base_address`` was set.  If the ``base_address``
attribute is not present the :class:`MemoryMapped

.. _module : http://docs.myhdl.org/en/stable/manual/structure.html#structural-modeling


Memory map interfaces
---------------------
The :Register Files: section examples eluded to the memory-map (or CSR)
interfaces and how they can be connected to register file.  The ``rhea``
project contains the following memory-map interfaces:

   * :class:`Barebone`
   * :class:`Wishbone`
   * :class:`AvalonMM`
   * :class:`AXI4Lite`

Each of these implement a memory-map bus type/specification and each
can be passed as and interface to a module.  Each of the specific
memory-mapped bus classes inherit the :class:`MemoryMapped` class.
The :class:`MemoryMapped` defines the attributes and methods the
memory-mapped buses have in common.

When interfacing to a register file, the register file is added to the
bus as shown in the previous example with the :func:`MemoryMapped.add`
function.  The register file covers many use cases for adding control
and status interfaces to different components.  Each interface also
contains a module to adapt the memory-map interface to a *generic*
interface.  In this case each bus is mapped to the :class:`Barebone`
bus with the :func:`MemoryMapped.map_to_generic`
function / `myhdl`_ `module`_.

The next section outlines how the :class:`RegisterFile` and the
corresponding registers is typically not used as defined above.  Rather,
an automated mapping of the control-status object is mapped to the
memory-space.  Software is used to encapsulate all the memory-based
accesses.


From attributes to bus cycles
-----------------------------
When designing a complex digital system with the ``rhea`` components
we don't want to deal with creating explict memory-maps.  We want to
interface with various modules through their control-status attributes.

As defined in the above first example, for our simple LED blinker
module there are a couple control signals defined.  The module can
be stimulated and controlled via this interface.  We might have some
external logic, or simply tie the module controls to physical inputs.

If we want to tie the controls to a register-file accessed by a
memory-mapped this


.. code-block:: python

   @myhdl.block
   def led_blinker(glbl, leds, membus=None, cso=None):

       if cso is None
           cso = led_blinker.cso()

       if membus is not None:
           rf = cso.get_register_file()
           membus.add(rf)

       # get any cso specific logic (if any)
       cso_inst = cso.get_generators()

       # ...

This gives a flexible mechanism to connect the module to a memory-mapped
bus or simply control the module through some other mechanism (e.g.
directly driven by the logic).

In the previous example all the explict addresses are hidden.  The
control-status attributes are accessed via the attributes (in simulation
and host software) and all the memory-mapped bus accesses are hidden.
The :class:`MemoryMap` has utilities to export the memory-map.


Static configuration
^^^^^^^^^^^^^^^^^^^^
The previous example demonstrated how the module can select to use the
external ``cso`` object, default ``cso``

