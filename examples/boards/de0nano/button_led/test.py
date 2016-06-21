
from __future__ import print_function

import pytest

import myhdl
from myhdl import Signal, intbv, instance, delay, StopSimulation

from button_led_mm import button_led_mm

from rhea.system import Clock
from rhea.system import Reset
from rhea.utils.test import run_testbench


def test_btn_led():

    clock = Clock(0, frequency=500e3)
    reset = Reset(0, active=0, async=False)
    leds = Signal(intbv(0)[8:])
    btns = Signal(intbv(0)[4:])

    @myhdl.build
    def bench_btn_led():

        # bus_type = ('A', 'B', 'W', 'X') # avalon, barebone, wishbone, AXI
        tbdut = button_led_mm(clock, reset, leds, btns, bus_type='wishbone')

        def dumpg(glist):
            for gg in glist:
                if isinstance(gg, (list,tuple)):
                    dumpg(gg)
                elif gg is not None:
                    print("{:16}:  {}".format(gg.func.__name__,
                                              gg.func.__module__))
        dumpg(tbdut)

        tbclk = clock.gen()

        @instance
        def tbstim():
            reset.next = reset.active
            yield delay(10)
            reset.next = not reset.active
            yield clock.posedge

            # assert leds == 0
            
            for ii in range(3):
                # simulate a button press
                btns.next = 1 << ii
                yield delay(12)
                btns.next = 0

                for cc in range(8):
                    yield clock.posedge
                    
                # @todo: a more interesting check
                # assert leds != 0
            yield delay(100)

            raise StopSimulation

        return tbdut, tbclk, tbstim

    run_testbench(bench_btn_led)
    # currently an error when converting to both at once,
    # only convert to one at a time.
    inst = button_led_mm(clock, reset, leds, btns)
    inst.convert(hdl='Verilog', directory='output')


if __name__ == '__main__':
    test_btn_led()
