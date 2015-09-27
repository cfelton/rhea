
from myhdl import Signal, instances

from ..misc import syncro
from ._uart import uartbaud, uarttx, uartrx


def uartlite(glbl, fbustx, fbusrx, serial_in, serial_out, baudrate=115200):
    """
    """
    clock, reset = glbl.clock, glbl.reset
    baudce, baudceh, baudce16 = [Signal(bool(0)) for _ in range(3)]
    tx, rx = Signal(bool(0)), Signal(bool(0))

    # create synchronizers for the input signals, the output
    # are not needed, guarantee IO registers
    instsyncrx = syncro(clock, serial_in, rx)
    instsynctx = syncro(clock, tx, serial_out)

    # generate a strobe for the desired baud rate
    instbaud = uartbaud(glbl, baudce, baudceh, baudce16,
                        baudrate=baudrate)

    # instantiate
    insttx = uarttx(glbl, fbustx, tx, baudce)
    instrx = uartrx(glbl, fbusrx, rx, baudce)

    return instances()
