
from pprint import pprint

from myhdl import *

import rhea.build as build
from rhea.build.boards import get_board


def m_button_led(clock,button,led):

    @always(clock.posedge)
    def rtl():
        led.next = button

    return rtl


def compile():
    brd = get_board('xula')
    # Set the ports for the design (top-level) and the
    # signal type for the ports.  If the port name matches
    # one of the FPGA default port names they do not need
    # to be remapped.
    brd.add_port('button', pins=(33,))
    brd.add_port('led', pins=(32,))
    
    flow = build.flow.ISE(brd=brd, top=m_button_led)
    flow.run()
    info = flow.get_utilization()
    pprint(info)
    

if __name__ == '__main__':
    compile()