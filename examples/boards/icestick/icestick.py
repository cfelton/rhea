
from __future__ import print_function, division

import myhdl
from myhdl import Signal, modbv, always, always_comb

from rhea.cores.uart import uartlite
from rhea.cores.misc import glbl_timer_ticks
from rhea.system import Global
from rhea.system import FIFOBus


@myhdl.block
def icestick(clock, led, pmod, uart_tx, uart_rx):
    """ Lattice Icestick example
    """
    
    glbl = Global(clock, None)    
    tick_inst = glbl_timer_ticks(glbl, include_seconds=True)

    # get interfaces to the UART fifos
    fbusrtx = FIFOBus(width=8)

    # get the UART comm from PC
    uart_inst = uartlite(glbl, fbusrtx, uart_tx, uart_rx)

    @always_comb
    def beh_loopback():
        fbusrtx.write_data.next = fbusrtx.read_data
        fbusrtx.write.next = (not fbusrtx.full) & fbusrtx.read

    lcnt = Signal(modbv(0, min=0, max=4))

    @always(clock.posedge)
    def beh_led_count():
        if glbl.tick_sec:
            lcnt.next = lcnt + 1;
        led.next = (1 << lcnt)

    # system to test/interface
    
    # other stuff

    return myhdl.instances()
