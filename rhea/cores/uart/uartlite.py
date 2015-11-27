
from myhdl import Signal, instances

from ..misc import syncro
from .uart import uartbaud, uarttx, uartrx
from ..fifo import fifo_fast


def uartlite(glbl, fbustx, fbusrx, serial_in, serial_out, baudrate=115200):
    """
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
