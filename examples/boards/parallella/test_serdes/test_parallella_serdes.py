
from __future__ import print_function, division

import pytest

import myhdl
from myhdl import Signal, intbv, always_comb
from myhdl import instance, delay, StopSimulation

from rhea.system import Clock, Reset
from rhea.utils.test import run_testbench, tb_args, tb_default_args

from parallella_serdes import parallella_serdes


@pytest.mark.xfail()
def test_parallella_serdes(args=None):
    args = tb_default_args(args)

    clock = Clock(0, frequency=50e6)
    reset = Reset(0, active=1, async=True)
    txp = Signal(intbv(0)[6:])
    txn = Signal(intbv(0)[6:])
    rxp = Signal(intbv(0)[6:])
    rxn = Signal(intbv(0)[6:])
    leds = Signal(intbv(0)[8:])

    @myhdl.block
    def bench_serdes():
        tbdut = parallella_serdes(clock, txp, txn, rxp, rxn, leds)
        tbclk = clock.gen(hticks=10000)

        @always_comb
        def tblpk():
            rxp.next = txp
            rxn.next = txn

        @instance
        def tbstim():
            yield reset.pulse(32)
            yield clock.posedge

            for ii in range(100):
                for jj in range(1000):
                    yield clock.posedge

            yield delay(1000)
            raise StopSimulation

        return tbdut, tbclk, tblpk, tbstim

    run_testbench(bench_serdes, timescale='1ps', args=args)
    inst = parallella_serdes(
        clock, txp, txn, rxp, rxn, leds
    )
    inst.convert(hdl='Verilog', directory='output', testbench=False)


if __name__ == '__main__':
    args = tb_args()
    test_parallella_serdes(args=args)
