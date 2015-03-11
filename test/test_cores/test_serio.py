
from myhdl import *

from mn.system import Clock,Reset
from mn.cores.misc import m_serio
from mn.utils.test import *

def test():
    clock = Clock(0)
    reset = Reset(0, active=0, async=False)
    sdi,sdo = [Signal(bool(0)) for _ in range(2)]
    pin = [Signal(intbv(0)[16:]) for _ in range(7)]
    pout = [Signal(intbv(0)[16:]) for _ in range(3)]

    def _test():
        tbclk = clock.gen()
        tbdut = m_serio(clock, reset, sdi, sdo, pin, pout)

        @instance
        def tbstim():
            yield reset.pulse(13)
            yield clock.posedge

            # @todo: actually test something
            for ii in range(1000):
                yield clock.posedge

            raise StopSimulation

        return tbdut, tbclk, tbstim

    Simulation(traceSignals(_test)).run()
