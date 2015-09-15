
from myhdl import (Signal, ResetSignal, intbv, always_seq, always,
                   always_comb)


def blinky(led, clock, reset=None):

    assert len(led) >= 2
    
    maxcnt = int(clock.frequency)
    cnt = Signal(intbv(0,min=0,max=maxcnt))
    toggle = Signal(bool(0))

    @always_seq(clock.posedge, reset=reset)
    def rtl():
        if cnt == maxcnt-1:
            cnt.next = 0
            toggle.next = not toggle
        else:
            cnt.next = cnt + 1

    @always_comb
    def rtl_assign():
        led.next[0] = toggle
        led.next[1] = not toggle
        
    if reset is None:
        reset = ResetSignal(0, active=0, async=False)

        @always(clock.posedge)
        def rtl_reset():
            reset.next = not reset.active
        g = (rtl, rtl_assign, rtl_reset,)
    else:
        g = (rtl, rtl_assign,)

    return g
