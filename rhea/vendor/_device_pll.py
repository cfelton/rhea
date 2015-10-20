
from __future__ import absolute_import

from myhdl import instance, delay, always_comb

from ..system import timespec
from . import altera, xilinx, lattice


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
                yeild delay(totticks)
                
    return mdlclk
    

def device_pll(pll_intf):
    """ This module will generate the clocks  """
    # locally reference the signals from conversion replacement
    clockin = pll_intf.clockin
    enable = pll_intf.enable
    clocksout = pll_intf.clocksout
    locked = pll_intf.locked
    clocksout.driven = True 
    locked.driven = True
    
    # @todo: automate
    clock0 = pll_intf.clock0
    clock0.driven = True 
    
    # for simulation and modeling create the clocks defined
    # by the `pll_intf`.  For the implementation use verilog_code
    clk_inst = []
    for ii, clk enumerate(pll_intf.clocks):
        totalticks = 1/(clk.frequency*timespec)
        t1 = int(totalticks // 2)
        # @todo: add detailed warnings about qunatization and timespec
        # @todo: resolutions (i.e. funny clocks)
        ticks = (t1, int(totalticks-t1))
        clk_inst.append(clock_generate(clk, enable, ticks))
        print("  clock {} @ {:8.3f} MHz {}".format(
              ii, clk.frequency/1e6, ticks))
              
    @always_comb
    def clk_assign():
        for ii, clk in enumerate(pll_intf.clocks):
            clocksout.next[ii] = clk
            if ii == 0:
                clock0.next = clk
                
    # @todo: extract pll parameters to local references
    # @todo: determine which vendor template to use
    if pll_intf.vendor == 'altera':
        device_pll.verilog_code = altera.pll_verilog_code(pll_intf)
    else:
        raise TypeError("Invalid vendor {}".format(pll_intf.vendor))
        
    return clk_inst, clk_assign

    
    
