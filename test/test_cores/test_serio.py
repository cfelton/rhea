
from myhdl import *

from rhea.system import Clock, Reset
from rhea.cores.misc import io_stub
from rhea.utils.test import tb_clean_vcd


def test():
    clock = Clock(0)
    reset = Reset(0, active=0, async=False)
    sdi, sdo = [Signal(bool(0)) for _ in range(2)]
    pin = [Signal(intbv(0)[16:]) for _ in range(7)]
    pout = [Signal(intbv(0)[16:]) for _ in range(3)]

    def _test():
        tbclk = clock.gen()
        tbdut = io_stub(clock, reset, sdi, sdo, pin, pout)

        @instance
        def tbstim():
            yield reset.pulse(13)
            yield clock.posedge

            # @todo: actually test something
            for ii in range(1000):
                yield clock.posedge

            raise StopSimulation

        return tbdut, tbclk, tbstim

    vcd = tb_clean_vcd('serio')
    traceSignals.name = vcd
    Simulation(traceSignals(_test)).run()


if __name__ == '__main__':
    test()