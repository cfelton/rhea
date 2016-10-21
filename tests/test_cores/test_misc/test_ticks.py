
from __future__ import print_function
from __future__ import division

import argparse

import myhdl
from myhdl import Signal, instance, now, StopSimulation

from rhea.system import Global, Clock, Reset
from rhea.cores.misc import glbl_timer_ticks
from rhea.utils.test import run_testbench


def test_ticks(args=None):
    user_ms = 16
    hticks = 5

    clock = Clock(0, frequency=10e3)
    reset = Reset(0, active=0, async=True)
    glbl = Global(clock, reset)

    @myhdl.block
    def bench_ticks():
        tbdut = glbl_timer_ticks(glbl, include_seconds=True, 
                                 user_timer=user_ms)
        tbclk = clock.gen(hticks=hticks)

        @instance
        def tbstim():
            yield reset.pulse(40)

            # sync up, start 1 second in (slow clock)
            yield glbl.tick_sec.posedge
            tickstart = now()

            yield glbl.tick_ms.posedge
            tickms1 = now()
            yield glbl.tick_ms.posedge
            tickms2 = now()

            yield glbl.tick_user.posedge
            tickuser1 = now()
            yield glbl.tick_user.posedge
            tickuser2 = now()

            yield glbl.tick_sec.posedge
            ticksec1 = now()
            yield glbl.tick_sec.posedge
            ticksec2 = now()
            
            sim_tick_ms = (clock.frequency/1000)*(hticks*2)

            assert (tickms2 - tickms1) == sim_tick_ms
            assert (tickuser2 - tickuser1) == sim_tick_ms*user_ms
            assert (ticksec2 - ticksec1) == sim_tick_ms*1000

            raise StopSimulation

        return tbdut, tbclk, tbstim

    run_testbench(bench_ticks)


if __name__ == '__main__':
    test_ticks()
