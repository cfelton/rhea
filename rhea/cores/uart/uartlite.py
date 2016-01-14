
from myhdl import Signal, instances

from ..misc import syncro
from .uartbase import uartbaud, uarttx, uartrx
from ..fifo import fifo_fast


def uartlite(glbl, fbustx, fbusrx, serial_in, serial_out, baudrate=115200):
    """ The top-level for a minimal fixed baud UART

    Ports
    -----
    glbl: rhea.Global interface, clock and reset from glbl
    fbustx: The transmit FIFO bus, interface to the TX FIFO
    tbusrx: The receive FIFObus, interface to the RX FIFO
    serial_in: The UART external serial line in
    serial_out: The UART external serial line out

    Parameters
    ----------
    baudrate: the desired baudrate for the UART

    Returns
    -------
    myhdl generators

    This module is myhdl convertible
    """
    clock, reset = glbl.clock, glbl.reset
    baudce, baudce16 = [Signal(bool(0)) for _ in range(2)]
    tx, rx = Signal(bool(1)), Signal(bool(1))

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

    return instances()
