
import myhdl
from myhdl import Signal, always_comb
from ..misc import syncro
from .uartbase import uartbaud, uarttx, uartrx
from ..fifo import fifo_fast
from rhea.system import FIFOBus


@myhdl.block
def uartlite(glbl, fifobus, serial_in, serial_out, baudrate=115200, fifosize=16):
    """ The top-level for a minimal fixed baud UART

    The function instantiates the various components required for
    the UART. Uses an external FIFOBus interface to communicate 
    with other modules(provide the r/w stobe, data etc.).

    Arguments(Ports):
        glbl: rhea.Global interface, clock and reset from glbl
        fbustx: The transmit FIFO bus, interface to the TX FIFO (see fifo_fast.py)
        tbusrx: The receive FIFObus, interface to the RX FIFO
        serial_in: The UART external serial line in
        serial_out: The UART external serial line out

    Parameters:
        baudrate: the desired baudrate for the UART

    This module is myhdl convertible
    """
    clock, reset = glbl.clock, glbl.reset
    baudce, baudce16 = [Signal(bool(0)) for _ in range(2)]
    tx, rx = Signal(bool(1)), Signal(bool(1))

    # the FIFO interfaces for each FIFO path
    fbustx = FIFOBus(fifobus.width)
    fbusrx = FIFOBus(fifobus.width)
    
    # create synchronizers for the input signals, the output
    # are not needed, guarantee IO registers
    syncrx_inst = syncro(clock, serial_in, rx)
    synctx_inst = syncro(clock, tx, serial_out)

    # FIFOs for tx and rx
    fifo_tx_inst = fifo_fast(glbl, fbustx, size=fifosize)
    fifo_rx_inst = fifo_fast(glbl, fbusrx, size=fifosize)

    # generate a strobe for the desired baud rate
    baud_inst = uartbaud(glbl, baudce, baudce16, baudrate=baudrate)

    # instantiate the UART paths
    tx_inst = uarttx(glbl, fbustx, tx, baudce)
    rx_inst = uartrx(glbl, fbusrx, rx, baudce16)

    # separate the general fifobus into two for transmitting and receiving

    @always_comb
    def assign_read():
        """Map external UART FIFOBus interface to internal
        Map the external UART FIFOBus interface attribute signals to
        internal RX FIFO interface.
        """
        # fifobus.read_data is the channel that the UART
        # reads data on and fifobus.write_data is the one
        # it writes to.
        # read into the fifobus from the RX fifo queue
        # whenever available by checking the queue
        fbusrx.read.next = fifobus.read
        fifobus.empty.next = fbusrx.empty
        fifobus.read_data.next = fbusrx.read_data
        fifobus.read_valid.next = fbusrx.read_valid

    @always_comb
    def assign_write():
        """Map external UART FIFOBus interface to internal
        Map external UART FIFOBus interface attribute signals to
        internal TX FIFO interface.
        """
        # queue to TX fifo whenever given ext. strobe
        # which will auto. be transferred by uarttx()
        fbustx.write.next = fifobus.write & (not fbustx.full)
        fbustx.write_data.next = fifobus.write_data
        fifobus.full.next = fbustx.full

    return myhdl.instances()
