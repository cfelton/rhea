
from myhdl import Signal, intbv, SignalType

from ..system import Clock
from . import Vendor

# keep track of the number of PLLInterfaces created
_pll_cnt = 0


class PLLClock(object):
    def __init__(self, clockin, clockout):
        self.clockin = clockin
        self.clockout = clockout
        

class PLLInterface(object):
    def __init__(self, clockin, reset=None, output_frequencies=None):
        """ An interface to various vendor embedded PLL primitives 
        This interface is used with the "vendor.*.pll" modules.  This 
        interface is intended to provide a generic interface to the 
        various implementations
        
        Ports:
          clockin: the input clock, thre frequency attribute is used.
          reset: optional
        Parameters:
          output_frequencies: A list of desired output frequencies.
          
        Example usage:
            clockext = Clock(0, frequency=50e6)
            resetext = Reset(0, active=0, async=True)
            pll_intf = PLLInterface(clockext, resetext,
                                    output_frequencies=(150e6, 200e6))
            pll_intf.model = brd.fpga
            pll_intf.vendor = vendor.altera
        """
        global _pll_cnt
        self.pll_num = _pll_cnt
        _pll_cnt += 1
        number_of_outputs = len(output_frequencies)

        self.clockin = clockin
        self.clockin_out = Signal(bool(0))
        self.input_frequency = clockin.frequency

        self.reset = reset
        self.enable = Signal(bool(0))
        self.output_frequencies = output_frequencies
        self.clocks = [Clock(0, f) for f in output_frequencies]
        self.clocksout = Signal(intbv(0)[number_of_outputs:])
        for ii, clk in enumerate(self.clocks):
            self.__dict__['clock{:02d}'.format(ii)] = clk
        self.locked = Signal(bool(0))
