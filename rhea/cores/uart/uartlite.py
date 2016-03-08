
from myhdl import Signal, instances, always_seq, always_comb
from ..misc import syncro
from .uartbase import uartbaud, uarttx, uartrx
from ..fifo import fifo_fast
from rhea.system import FIFOBus


def uartlite(glbl, fifobus, serial_in, serial_out, baudrate=115200):
    """ The top-level for a minimal fixed baud UART

    Ports
    -----
        glbl: rhea.Global interface, clock and reset from glbl
        fbustx: The transmit FIFO bus, interface to the TX FIFO (see fifo_fast.py)
        tbusrx: The receive FIFObus, interface to the RX FIFO
        serial_in: The UART external serial line in
        serial_out: The UART external serial line out

    Parameters
    ----------
        baudrate: the desired baudrate for the UART

    Returns
    -------
        myhdl generators
        instsyncrx, instsynctx : syncs of external r/w line to the internal r/t
        insttxfifo, instrxfifo : The actual TX and RX fifos
        instbaud : baud strobe instantiation
        insttx, instrx : uart tx and rx generators
        sync_read,sync_write : convert one ext. Fbus to dual, for r/w

    This module is myhdl convertible
    """
    clock, reset = glbl.clock, glbl.reset
    baudce, baudce16 = [Signal(bool(0)) for _ in range(2)]
    tx, rx = Signal(bool(1)), Signal(bool(1))
    fbusrx = FIFOBus(fifobus.size, fifobus.width)
    fbustx = FIFOBus(fifobus.size, fifobus.width)
    
    # create synchronizers for the input signals, the output
    # are not needed, guarantee IO registers
    instsyncrx = syncro(clock, serial_in, rx)
    instsynctx = syncro(clock, tx, serial_out)

    # FIFOs for tx and rx
    insttxfifo = fifo_fast(clock, reset, fbustx)
    instrxfifo = fifo_fast(clock, reset, fbusrx)

    # generate a strobe for the desired baud rate
    instbaud = uartbaud(glbl, baudce, baudce16, baudrate=baudrate)

    # instantiate
    insttx = uarttx(glbl, fbustx, tx, baudce)
    instrx = uartrx(glbl, fbusrx, rx, baudce16)

    # separate the general fifobus into two
    # for transmitting and receiving

    @always_comb
    def sync_read():
        # fifobus.read_data is the channel that the UART 
        # reads data on and fifobus.write_data is the one 
        # it writes to.
        # read into the fifobus from the RX fifo queue 
        # whenever available by ckecking the queue
        fifobus.empty.next = fbusrx.empty
        fifobus.read_data.next = fbusrx.read_data       
        fifobus.read.next = not fbusrx.empty  
        fbusrx.read.next = not fbusrx.empty  
        fifobus.read_valid.next = fbusrx.read_valid

    @always_comb
    def sync_write():
        # queue to TX fifo whenever given ext. strobe
        # which will auto. be transferred by uarttx()
        fifobus.full.next = fbustx.full
        fbustx.write_data.next = fifobus.write_data
        fbustx.write.next = fifobus.write & (not fbustx.full )
        
         
    return instances()
