
from __future__ import print_function
from __future__ import division

import os
import argparse

import myhdl
from myhdl import (Signal, ResetSignal, intbv, instance,
                   always, always_seq, always_comb, delay)

from rhea.system import Clock
from rhea.system import timespec, ticks_per_ns
from rhea.vendor import ClockManagement
from rhea.vendor import device_clock_mgmt
from rhea.utils.test import run_testbench, tb_args, tb_default_args, tb_convert


@myhdl.block
def top_clock_mgmt_wrap(clockext, resetext, dripple, status, args):
    # note: the model will have errors for many frequencies the test
    # will only work for rational periods (inverse of the freq).
    clkmgmt = ClockManagement(clockext, reset=resetext,
                              output_frequencies=(125e6, 200e6,))
    clkmgmt.vendor = args.vendor

    # @todo: add external_reset_sync module
    # rst_inst = external_reset_sync(clockext, resetext, reset)

    # create the pll instance
    pll_inst = device_clock_mgmt(clkmgmt)

    clockcsr = Signal(bool(0))
    clockdat = Signal(bool(0))
    dcnt = Signal(intbv(0, min=0, max=int(clkmgmt.clocks[0].frequency/1e6)))
    dmax = dcnt.max

    @always_comb
    def beh_clock_assign():
        clockcsr.next = clkmgmt.clocksout[0]
        clockdat.next = clkmgmt.clocksout[1]

    @always(clockext.posedge)
    def beh_assign():
        clkmgmt.enable.next = True

    @always_seq(clockcsr.posedge, reset=resetext)
    def beh_cnt():
        if dcnt == dmax-1:
            dcnt.next = 0
            dripple.next = not dripple
        else:
            dcnt.next = dcnt + 1

    @always_seq(clockdat.posedge, reset=resetext)
    def beh_led_drv():
        status.next[0] = clkmgmt.locked

    return pll_inst, beh_assign, beh_clock_assign, beh_cnt, beh_led_drv


def test_device_clock_mgmt(args=None):
    args = tb_default_args(args)
    if not hasattr(args, 'vendor'):
        args.vendor = 'altera'
    clockext = Clock(0, frequency=50e6)
    resetext = ResetSignal(0, active=0, async=True)
    dripple = Signal(bool(0))
    status = Signal(intbv(0)[4:])

    @myhdl.block
    def bench_device_pll():
        tbdut = top_clock_mgmt_wrap(clockext, resetext, dripple,
                                    status, args)

        @always(delay(10*ticks_per_ns))
        def tbclk():
            clockext.next = not clockext

        @instance
        def tbstim():
            resetext.next = not resetext.active
            yield delay(33*ticks_per_ns)

            for ii in range(3):
                yield dripple.posedge
                ts = myhdl.now()
                yield dripple.posedge
                td = myhdl.now() - ts
                yield delay(100*ticks_per_ns)
                print(td, 2*ticks_per_ns*1e3)
                # assert td == 2 * ticks_per_ns * 1e3

            yield delay(100*ticks_per_ns)

            raise myhdl.StopSimulation

        return tbdut, tbclk, tbstim

    run_testbench(bench_device_pll, args=args)
    inst = top_clock_mgmt_wrap(clockext, resetext, dripple, status, args)
    inst.convert(hdl="Verilog", directory="output")


if __name__ == '__main__':
    args = tb_args()
    args.vendor = 'altera'
    test_device_clock_mgmt(args)
