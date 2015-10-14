
from __future__ import print_function
from __future__ import division

from myhdl import (Signal, intbv, modbv, always, always_comb,
                   instances)

from rhea.cores.uart import uartlite
from rhea.cores.misc import glbl_timer_ticks
from rhea.system import Global
from rhea.system import FIFOBus


def icestick(clock, led, pmod, uart_tx, uart_rx):
    """ Lattice Icestick example
    """
    
    glbl = Global(clock, None)    
    gticks = glbl_timer_ticks(glbl, include_seconds=True)

    # get interfaces to the UART fifos
    fbustx = FIFOBus(width=8, size=8)
    fbusrx = FIFOBus(width=8, size=8)

    # get the UART comm from PC
    guart = uartlite(glbl, fbustx, fbusrx, uart_tx, uart_rx)

    @always_comb
    def beh_loopback():
        fbusrx.rd.next = not fbusrx.empty
        fbustx.wr.next = not fbusrx.empty
        fbustx.wdata.next = fbusrx.rdata

    lcnt = Signal(modbv(0, min=0, max=4))
    @always(clock.posedge)
    def beh_led_count():
        if glbl.tick_sec:
            lcnt.next = lcnt + 1;
        led.next = (1 << lcnt)

    # system to test/interface
    
    # other stuff

    return instances()