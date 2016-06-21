
import argparse
from pprint import pprint 

import myhdl
from myhdl import (Signal, ResetSignal, intbv, always_seq, always,
                   always_comb)

from rhea.build.boards import get_board
                   

led_port_pin_map = {
    'xula':  dict(name='led', pins=(32,)),
    'xula2': dict(name='led', pins=('R7',)),
}


@myhdl.block
def xula_blinky(led, button, clock, reset=None):
    """ a simple LED blinks example.
    This is intended to be used with the Xula, Stickit motherboard
    and an LED / button pmod board.
    """    
    maxcnt = int(clock.frequency)
    cnt = Signal(intbv(0, min=0, max=maxcnt))
    toggle = Signal(bool(0))
    
    @always_seq(clock.posedge, reset=None)
    def beh():
        if cnt == maxcnt-1:
            toggle.next = not toggle
            cnt.next = 0 
        else:
            cnt.next = cnt + 1 
            
    @always_comb
    def beh_assign():
        if not button:
            led.next = True
        else:
            led.next = toggle
        
    return beh, beh_assign
    
        
def build(args):
    brd = get_board(args.brd)
    # the design port names don't match the board pin names,
    # add the ports here (all the IO are a generic "chan")
    brd.add_port(**led_port_pin_map[args.brd])
    brd.add_port(name='button', pins=(33,))
    flow = brd.get_flow(xula_blinky)
    flow.run()
    info = flow.get_utilization()
    pprint(info)
    
    
def cliparse():
    parser = argparse.ArgumentParser()
    parser.add_argument("--brd", default='xula')
    parser.add_argument("--flow", default="ise")
    args = parser.parse_args()
    return args
    
    
def main():
    args = cliparse()
    build(args)
    
        
if __name__ == '__main__':
    main()
