

import myhdl
from myhdl import Signal, intbv, instance, delay, StopSimulation

from rhea.system import Clock, Reset
from rhea.utils.test import run_testbench, tb_args, tb_default_args

from zybo_device_primitives import zybo_device_prim


def test_devprim(args=None):
    args = tb_default_args(args)
    clock = Clock(0, frequency=125e6)
    reset = Reset(0, active=0, async=True)
    leds = Signal(intbv(0)[4:])

    @myhdl.block
    def bench_devprim():
        tbdut = zybo_device_prim(clock, leds, reset)
        tbclk = clock.gen(hticks=10000)

        @instance
        def tbstim():
            print("start simulation")
            yield reset.pulse(36)
            yield clock.posedge
            for ii in range(40):
                yield delay(11111)
            print("end simulation")
            raise StopSimulation

        return tbdut, tbclk, tbstim

    run_testbench(bench_devprim, args=args)

