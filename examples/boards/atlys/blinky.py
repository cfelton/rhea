
import argparse
import myhdl
from myhdl import (Signal, intbv, always_seq, always_comb)

from rhea.build.boards import get_board


@myhdl.blink
def atlys_blinky(led, clock, reset=None):
    """ simple de0nano LED blink """
    assert len(led) == 8

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
        led.next[0] = toggle
        led.next[1] = not toggle
        for ii in range(2, 8):
            led.next[ii] = 0

    return beh, beh_assign


def build(args):
    brd = get_board('atlys')
    flow = brd.get_flow(top=atlys_blinky)
    flow.run()


def cliparse():
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    return args


def main():
    args = cliparse()
    build(args)


if __name__ == '__main__':
    main()
