

from __future__ import division
import myhdl
from myhdl import Signal, intbv, always_seq, always


@myhdl.block
def timer_counter(glbl, counter, increment, overflow):
    clock, reset = glbl.clock, glbl.reset
    count_max = counter.max

    @always_seq(clock.posedge, reset=reset)
    def beh_count():
        if increment:
            if counter == count_max - 1:
                counter.next = 0
            else:
                counter.next = counter + 1

    @always(clock.posedge)
    def beh_overflow():
        if increment and counter == count_max-2:
            overflow.next = True
        else:
            overflow.next = False

    return beh_count, beh_overflow


@myhdl.block
def glbl_timer_ticks(glbl, include_seconds=True, user_timer=None, tick_div=1):
    """ generate 1 ms and 1 sec ticks

    Arguments:
        glbl (Global): global interface to attach the time ticks

    Parameters:
        include_seconds (bool): generate the one second tick
        user_timer (int): generate a custom timer tick in milliseconds
        tick_div: used for simulation, shorten the actual tick period
    """
    gens = tuple()

    clock, reset = glbl.clock, glbl.reset

    # define the number of clock ticks per strobe
    ticks_per_ms = int(glbl.clock.frequency//1000)
    ms_per_sec = 1000
    ms_per_user = int(user_timer) if user_timer is not None else 1

    # simulation mode, remove the dead time, the ticks
    # will be considerably shorter than actual
    if tick_div > 1:
        ticks_per_ms = int(ticks_per_ms // tick_div)

    # check that the range limits are valid
    assert ticks_per_ms > 0 and ms_per_sec > 0 and ms_per_user > 0, \
        "counts must be greater than zero: {}, {}, {}".format(
            ticks_per_ms, ms_per_sec, ms_per_user)
    
    mscnt = Signal(intbv(0, min=0, max=ticks_per_ms))
    seccnt = Signal(intbv(0, min=0, max=ms_per_sec))
    usercnt = Signal(intbv(0, min=0, max=ms_per_user))

    t1_inst = timer_counter(glbl, counter=mscnt, increment=True,
                            overflow=glbl.tick_ms)

    if include_seconds:
        t2_inst = timer_counter(glbl, counter=seccnt,
                                increment=glbl.tick_ms,
                                overflow=glbl.tick_sec)
    else:
        glbl.tick_sec = None
        t2_inst = []

    if user_timer is not None:
        t3_inst = timer_counter(glbl, counter=usercnt,
                                increment=glbl.tick_ms,
                                overflow=glbl.tick_user)
    else:
        glbl.tick_user = None
        t3_inst = []

    return t1_inst, t2_inst, t3_inst
