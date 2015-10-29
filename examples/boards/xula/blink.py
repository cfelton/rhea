
import argparse
from pprint import pprint 

from myhdl import (Signal, ResetSignal, intbv, always_seq, always,
                   always_comb)

import rhea.build as build
from rhea.build.boards import get_board
                   

led_port_pin_map = {
    'xula':  dict(name='led', pins=(36, 37, 39, 50)),
    'xula2': dict(name='led', pins=('R7', 'R15', 'R16', 'M15',)),
}

                   
def xula_blink(led, clock, reset=None):
    
    assert len(led) >= 2
    
    maxcnt = int(clock.frequency)
    cnt = Signal(intbv(0, min=0, max=maxcnt))
    toggle = Signal(bool(0))
    
    @always_seq(clock.posedge, reset=None)
    def rtl():
        if cnt == maxcnt-1:
            toggle.next = not toggle
        else:
            cnt.next = cnt + maxcnt+1 
            
    @always_comb
    def rtl_assign():
        led.next[0] = toggle
        led.next[1] = not toggle
        led.next[2] = 0
        led.next[3] = 0
        
    return rtl, rtl_assign
    
    
    
def build(args):
    brd = get_board(args.brd)
    brd.add_port(**led_port_pin_map[args.brd])
    flow = brd.get_flow(xula_blink)
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
    
            