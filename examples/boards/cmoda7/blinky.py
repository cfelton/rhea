
import myhdl
from myhdl import (Signal, intbv, always_seq, always_comb, concat)

from rhea.build.boards import get_board

#variant = '15t'    # define to use the 'cmoda7_15t' variant
variant = '35t'     # define to use the 'cmoda7_35t' variant

@myhdl.block
def cmoda7_blink(led, btn, clock):
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
            led.next = True
        else:
            led.next = toggle

    return rtl, rtl_assign


def build():
    brd = get_board('cmoda7_' + variant)
    assert brd
    flow = brd.get_flow(cmoda7_blink)
    flow.run()
    

def main():
    build()


if __name__ == '__main__':
    main()
