
import os 
from argparse import Namespace

import myhdl
from myhdl import *

from rhea.system import Clock, Reset
from rhea.cores.misc import io_stub
from rhea.utils.test import run_testbench, tb_convert


def test(args=None):
    if args is None:
        args = Namespace(trace=False)

    clock = Clock(0, frequency=50e6)
    reset = Reset(0, active=0, async=False)
    sdi, sdo = [Signal(bool(0)) for _ in range(2)]

    pin = [Signal(intbv(0)[16:]) for _ in range(1)]
    pout = [Signal(intbv(0)[16:]) for _ in range(3)]
    valid = Signal(bool(0))

    def bench_serio():
        tbclk = clock.gen()
        tbdut = io_stub(clock, reset, sdi, sdo, pin, pout, valid)

        @instance
        def tbstim():
            yield reset.pulse(13)
            yield clock.posedge

            for pp in pout:
                pp.next = 0

            sdi.next = False
            yield delay(200)
            yield clock.posedge

            for ii in range(1000):
                yield clock.posedge
                assert sdo == False
            assert pin[0] == 0

            for pp in pout:
                pp.next = 0xFFFF
            sdi.next = True
            yield valid.posedge
            yield delay(200)
            yield clock.posedge

            for ii in range(1000):
                yield clock.posedge
                assert sdo == True
            assert pin[0] == 0xFFFF

            raise StopSimulation

        return tbdut, tbclk, tbstim

    run_testbench(bench_serio, args=args)

    # a top-level conversion stub
    def top_stub(clock, reset, sdi, sdo):
        pin = [Signal(intbv(0)[16:0]) for _ in range(1)]
        pout = [Signal(intbv(0)[16:0]) for _ in range(3)]
        valid = Signal(bool(0))
        stub_inst = io_stub(clock, reset, sdi, sdo, pin, pout, valid)
        return stub_inst

    # convert the design stub 
    tb_convert(top_stub, clock, reset, sdi, sdo)


if __name__ == '__main__':
    args = Namespace(trace=True)
    test(args)
