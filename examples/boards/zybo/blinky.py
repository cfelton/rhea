
import myhdl
from myhdl import (Signal, intbv, always_seq, always_comb, concat)

from rhea.build.boards import get_board


@myhdl.block
def zybo_blink(led, btn, clock):
    maxcnt = int(clock.frequency)
    cnt = Signal(intbv(0, min=0, max=maxcnt))
    toggle = Signal(bool(0))

    @always_seq(clock.posedge, reset=None)
    def rtl():
        if cnt == maxcnt-1:
            toggle.next = not toggle
            cnt.next = 0
        else:
            cnt.next = cnt + 1

    @always_comb
    def rtl_assign():
        if btn:
            led.next = btn
        else:
            led.next = concat("000", toggle)

    return rtl, rtl_assign


def build():
    brd = get_board('zybo')
    flow = brd.get_flow(zybo_blink)
    flow.run()
    

def main():
    build()


if __name__ == '__main__':
    main()
