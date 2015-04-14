
from __future__ import print_function

import argparse

from myhdl import *

import gizflo as flo

from mn.cores.misc import m_btn_mm_ctl   # memmap controller
from mn.cores.misc import m_led_mm_per   # memmap peripheral

from mn.system import Barebone
from mn.system import Wishbone
from mn.system import AvalonMM
#from mn.system import AXI4
from mn.system import Global


def m_btn_led_mm(clock, reset, leds, btns, bus_type='W'):
    """ A toy example to demostrate bus agnosticism
    This example instantiates a memory-map controller and a
    memory-map peripheral.  This example shows how the 
    controllers and peripherals can be passed the memmap
    interface.  The passing of the interface allows the 
    modules (components) to be bus agnostic.

    This example solves a simple task in a complicated manner
    to show the point.  When a button press is detected a 
    bus cycle is generated to write the "flash" pattern to 
    the LED peripheral.

    Note: for easy FPGA bit-stream generation the port names
    match the board names defined in the *gizflo* board definitions.
    """
    glbl = Global(clock=clock, reset=reset)

    if bus_type == 'B':
        regbus = Barebone(glbl, data_width=8, address_width=16)
    elif bus_type == 'W':
        regbus = Wishbone(glbl, data_width=8, address_width=16)
    elif bus_type == 'A':
        regbus = AvalonMM(glbl, data_width=8, address_width=16)
    #elif bus_type == 'X':
    #    regbus = AXI4(glbl, data_wdith=8, address_width=16)

    gbtn = m_btn_mm_ctl(glbl, regbus, btns)  # memmap controller
    gled = m_led_mm_per(glbl, regbus, leds)  # memmap peripheral
    gmap = regbus.m_per_outputs()            # bus combiner

    print(vars(regbus.regfiles['LED_000']))

    return gbtn, gled, gmap


def build(args):
    """ Run the FPGA tools
    """
    pass


def getargs():
    """ get CLI arguments
    """
    pass


if __name__ == '__main__':
    args = getargs()
    build(args)

    

    