
from myhdl import *

def m_blink(toggle, clock, reset=None):

    MAX_CNT = int(clock.frequency)
    cnt = Signal(intbv(0,min=0,max=MAX_CNT))

    @always_seq(clock.posedge, reset=reset)
    def rtl():
        if cnt == MAX_CNT-1:
            cnt.next = 0
            toggle.next = not toggle
        else:
            cnt.next = cnt + 1

    if reset is None:
        reset = ResetSignal(0, active=0, async=False)

        @always(clock.posedge)
        def rtl_reset():
            reset.next = not reset.active
        g = (rtl,rtl_reset,)
    else:
        g = rtl

    return g
