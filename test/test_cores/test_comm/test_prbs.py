
from __future__ import print_function
from __future__ import division

from myhdl import Signal, intbv, instance, delay, StopSimulation, now
from rhea.system import Global, Clock, Reset
from rhea.cores.comm import prbs_generate
from rhea.utils.test import run_testbench, tb_args, tb_default_args


def test_known_prbs7(args=None):
    args = tb_default_args(args)
    clock = Clock(0, frequency=125e6)
    reset = Reset(0, active=1, async=False)
    glbl = Global(clock, reset)
    prbs = Signal(intbv(0)[8:])

    expected_pattern = (0x7F, 0x20, 0x18, 0x8A, 0x27, 0x9A, 0x2B, 0x5F,
                        0x38, 0x92, 0xAd, 0xBD, 0xB1, 0x74, 0x67, 0xAA)

    def _bench_prbs():
        tbdut = prbs_generate(glbl, prbs, order=7, initval=0x7F)
        tbclk = clock.gen(hticks=8000)

        @instance
        def tbstim():
            yield reset.pulse(32)
            # there is one zero at the beginning
            #yield clock.posedge
            yield clock.posedge
            yield delay(1)

            for ii, ep in enumerate(expected_pattern):
                print("{:12d}: {:02X} {:02X}".format(now(), int(prbs), ep))
                # assert prbs == ep
                yield clock.posedge
                yield delay(1)
                if ii == 2:
                    break

            yield delay(100)
            raise StopSimulation

        return tbdut, tbclk, tbstim

    run_testbench(_bench_prbs, timescale='1ps', args=args)


def test_prbs(args=None):
    args = tb_default_args(args)
    clock = Clock(0, frequency=125e6)
    reset = Reset(0, active=1, async=False)
    glbl = Global(clock, reset)
    prbs = Signal(intbv(0)[8:])

    def _bench_prbs():
        # currently only order 7, 9, 11, 15, 23, and 31 are coded in
        # prbs feedback tap table, limit testing to one of these patterns
        tbdut = prbs_generate(glbl, prbs, order=23)
        tbclk = clock.gen(hticks=8000)

        @instance
        def tbstim():
            yield reset.pulse(32)

            for ii in range(27):
                print("{:12d}: {:02X}".format(now(), int(prbs)))
                yield clock.posedge
                yield delay(1)

            yield delay(100)
            raise StopSimulation

        return tbdut, tbclk, tbstim


def tb_parser():
    pass


if __name__ == '__main__':
    args = tb_args()  # tb_args(parser=tb_parser())
    test_prbs(args)
    test_known_prbs7(args)

