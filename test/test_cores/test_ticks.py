
from __future__ import print_function
from __future__ import division

import argparse

from myhdl import *

from rhea.system import Global, Clock, Reset
from rhea.cores.misc import glbl_timer_ticks
from rhea.utils.test import tb_clean_vcd

def test_ticks():
    tb_ticks(args=argparse.Namespace())


def tb_ticks(args=None):
    user_ms = 16
    hticks = 5

    clock = Clock(0, frequency=10e3)
    reset = Reset(0, active=0, async=True)
    glbl = Global(clock, reset)

    def _bench():
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
            
            # @todo: figure out if the sim ticks are correct
            # 10k*10 per ms
            sim_tick_ms = (clock.frequency/1000)*(hticks*2)

            assert (tickms2 - tickms1) == sim_tick_ms
            assert (tickuser2 - tickuser1) == sim_tick_ms*user_ms
            assert (ticksec2 - ticksec1) == sim_tick_ms*1000

            raise StopSimulation

        return tbdut, tbclk, tbstim
    
    vcd = tb_clean_vcd(tb_ticks.__name__)
    traceSignals.name = vcd
    traceSignals.timescale = '{:d}us'.format(int((1/clock.frequency)/10))
    Simulation(traceSignals(_bench)).run()


if __name__ == '__main__':
    test_ticks()