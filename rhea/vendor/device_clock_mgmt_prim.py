
from __future__ import absolute_import

import myhdl
from myhdl import instance, delay, always_comb

from rhea.system import timespec


@myhdl.block
def _clock_generate(clock, enable, ticks):
    assert len(ticks) == 2
    totticks = sum(ticks)

    @instance
    def mdlclk():
        clock.next = False
        while True:
            if enable:
                yield delay(ticks[0])
                clock.next = True
                yield delay(ticks[1])
                clock.next = False
            else:
                yield delay(totticks)

    return mdlclk


@myhdl.block
def device_clock_mgmt_prim(clkmgmt):
    """ This is the generic device PLL model
    The vendor specific implementations will set the v*_code attribute
    for this function to the specific template needed to instantiate
    the device primitive in the generated intermediate V*.  This
    block also creates the clocks for MyHDL simulation when the device
    primitives are not available.
    
    not convetible, simulation only.
    """
    pif = clkmgmt
    (clockin, reset, enable,
     clocksout, locked,) = (pif.clockin, pif.reset, pif.enable,
                            pif.clocksout, pif.locked,)
    clocksout.driven = True
    locked.driven = True

    # for simulation and modeling create the clocks defined
    # by the `pll_intf`.  For the implementation use verilog_code
    clk_inst = []
    for ii, clk in enumerate(clkmgmt.clocks):
        totalticks = 1/(clk.frequency*timespec)
        t1 = int(totalticks // 2)
        # @todo: add detailed warnings about qunatization and timespec
        # @todo: resolutions (i.e. funny clocks)
        ticks = (t1, int(totalticks-t1))
        clk_inst.append(_clock_generate(clk, enable, ticks))
        print("  clock {} @ {:8.3f} MHz {}".format(
              ii, clk.frequency/1e6, ticks))

    @always_comb
    def clk_assign():
        clkmgmt.clockin_out.next = clockin
        for ii, clk in enumerate(clkmgmt.clocks):
            clocksout.next[ii] = clk

    return clk_inst, clk_assign
