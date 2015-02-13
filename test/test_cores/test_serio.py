
from myhdl import *

from mn.system import Clock,Reset
from mn.cores import serio

def test():
    clock = Clock(0)
    reset = Reset(0, 0, False)

    def _test():
        tbclk = Clock.gen()

        @instance
        def tbstim():
            yield reset.pulse(13)
            yield clock.posedge

        return tbdut, tbclk, tbstim

    Simulation(traceSignals(_test)).run()
