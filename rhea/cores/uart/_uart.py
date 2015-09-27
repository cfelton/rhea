
from fractions import gcd

from myhdl import Signal, intbv, always_seq


def uartbaud(glbl, baudce, baudceh, baudce16, baudrate=115200):
    """ Generate the UART baudrate strobe
    Three separate strobes are create: baudce, baudceh
    """
    clock, reset = glbl.clock, glbl.reset

    # determine the actual baud rate given the system clock and then
    # calculate the limit
    baudfreq = int((16*baudrate) / (gcd(clock.frequency, 16*baudrate)))
    baudlimit = int((clock.frequency / gcd(clock.frequency, 16*baudrate))
                    - baudfreq)

    print("uartlite: baud frequency {:f} baud limit {:d}".format(
          baudfreq, baudlimit))

    cnt = Signal(intbv(0, min=0, max=baudlimit))

    @always_seq(clock.posedge, reset=reset)
    def rtlbaud():
        if cnt >= baudlimit:
            cnt.next = cnt - baudlimit

    return rtlbaud


def uarttx(glbl, fbustx, tx, baudce):
    """ """
    clock, reset = glbl.clock, glbl.reset

    @always_seq(clock.posedge, reset=reset)
    def rtltx():
        tx.next = True

    return rtltx


def uartrx(glbl, fbusrx, rx, baudce):
    """ """
    clock, reset = glbl.clock, glbl.reset

    @always_seq(clock.posedge, reset=reset)
    def rtlrx():
        fbusrx.wr.next = False

    return rtlrx
