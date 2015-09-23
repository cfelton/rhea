
from __future__ import print_function
from __future__ import division

from myhdl import Signal, intbv, instances

from rhea.cores.uart import uart_lite
from rhea.cores.misc import glbl_timer_ticks
from rhea.system impor Global
from rhea.system import FIFOBus


def icestick(
    # ports
    clock, reset, led, pmod, 
    uart_tx, uart_rx
    # parameters
):
    """
    """
    
    glbl = Global(clock, reset)    
    gticks = glbl_timer_ticks(glbl, include_seconds=True)

    # get interfaces to the UART fifos
    fbustx, fbusrx = (FIFOBus(width=8, size=8), 
                      FIFOBus(width=8, size=8), )

    # get the UART comm from PC
    guart = uart_lite(glbl, fbustx, fbusrx, uart_tx, uart_rx)

    # system to test/interface
    
    # other stuff

    return instances()