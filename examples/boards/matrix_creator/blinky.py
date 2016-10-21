
from pprint import pprint

import myhdl
from myhdl import Signal, intbv, always_seq, always_comb

from rhea.build.boards import get_board


@myhdl.block
def mc_blinky(led, clock, reset):
    maxcnt = int(clock.frequency)
    cnt = Signal(intbv(0, min=0, max=maxcnt))
    toggle = Signal(bool(0))

    @always_seq(clock.posedge, reset=reset)
    def beh():
        if cnt == maxcnt-1:
            toggle.next = not toggle
            cnt.next = 0
        else:
            cnt.next = cnt + 1

    @always_comb
    def beh_outputs():
        led.next = toggle

    return myhdl.instances()


def build():
    brd = get_board('matrix_creator')
    flow = brd.get_flow(mc_blinky)
    flow.run()
    info = flow.get_utilization()
    pprint(info)