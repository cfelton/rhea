
Memory Map Utilities
====================
The ``rhea`` package contains a framework for managing the
memory-mapped control, status, and data access (most often,
simply control and status).  The following are various
memory-map utilities and peripherals.


Command bridge
--------------
The `command_bridge` provides a mechanism to generate memory-mapped
bus cycles from a received *packet*.  This provides a low-level
external access to the internal memory-space.

The ``command_bridge`` uses ``FIFOBus`` interface to receive
command packets and a ``FIFOBus`` to send response packets.
The ``comand_briged`` sends a response packet for every command
packet received.

The ``command_bridge`` can be used with any external interface that
can source packets to the ``FIFIBus`` interface and sink packets
from a ``FIFOBus`` interface.

.. autofunction:: rhea.cores.memmap.command_bridge


Note, most of the memory-map peripherals in the `rhea` package are
not designed to specific memory-space addresses.  The cores are
designed with a ``ControlStatus`` (control-status-object: cso)
interface that contains attributes
which are the control and status signals to the module.  These
signals are automatically assigned a location in the memory-space.
When working in Python the
addresses are completely abstracted away when not using the
``cso`` the addresses need to be exported from the system and
used explicitly.


Example
^^^^^^^
The following is an example that connects a ``command_bridge`` to a
UART.

.. code-block::python


    from rhea.system import Global, Wishbone, FIFOBus
    from rhea.memmap import command_bridge
    from rhea.memmap import peripheral
    from rhea.uart import uartlite

    def my_packet_to_memory_space(clock, reset, uart_rx, uart_tx):

        glbl = Global(clock, reset)
        rxpkt, txpkt = FIFOBus(), FIFOBus()
        csbus = Wishbone(data_width=32, address_width=32)

        uart_inst = uartlite(glbl, txpkt, rxpkt, uart_rx, uart_tx)
        cmd_inst = command_birdge(glbl, rxpkt, txpkt, csbus)
        per1_inst = peripheral(glbl, csbus)
        per2_inst = peripheral(glbl, csbus)

        return uart_inst, cmd_inst, per1_inst, per2_inst

