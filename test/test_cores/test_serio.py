
from myhdl import *

from rhea.system import Clock, Reset
from rhea.cores.misc import io_stub
from rhea.utils.test import run_testbench


def test():
    clock = Clock(0)
    reset = Reset(0, active=0, async=False)
    sdi, sdo = [Signal(bool(0)) for _ in range(2)]
    pin = [Signal(intbv(0)[16:]) for _ in range(7)]
    pout = [Signal(intbv(0)[16:]) for _ in range(3)]
    valid = Signal(bool(0))

    def _bench_serio():
        tbclk = clock.gen()
        tbdut = io_stub(clock, reset, sdi, sdo, pin, pout, valid)

        @instance
        def tbstim():
            yield reset.pulse(13)
            yield clock.posedge

            # @todo: actually test something
            for ii in range(1000):
                yield clock.posedge

            raise StopSimulation

        return tbdut, tbclk, tbstim

    run_testbench(_bench_serio)


if __name__ == '__main__':
    test()