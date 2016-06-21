
from myhdl import Signal, intbv
from rhea.system import Clock


_clkmgmt_cnt = 0


class ClockManagement(object):
    def __init__(self, clockin, reset=None, output_frequencies=None,
                 vendor='none'):
        """  An interface to various vendor clock generators.
        Most FPGA have a DLL/PLL/MMCM or some kind of primitive to generate
        clocks.  This interface is used to generically create clocks in a
        design.  The device specific primitives will be generated based on
        the attributes of this interface (object).

        This interface is used with the vendor.*.device_clock_mgmt modules.

        Ports:
          clockin: the input clock, thre frequency attribute is used.
          reset: optional

        Parameters:
          output_frequencies: A list of desired output frequencies.

        Example usage:
            clockext = Clock(0, frequency=50e6)
            resetext = Reset(0, active=0, async=True)
            clkmgmt = ClockManagement(clockext, resetext,
                                      output_frequencies=(150e6, 200e6))
            clkmgmt.model = brd.fpga
            clkmgmt.vendor = vendor.altera

        """
        global _clkmgmt_cnt
        self.clkmgmt_num = _clkmgmt_cnt
        _clkmgmt_cnt += 1
        number_of_outputs = len(output_frequencies)
        self.vendor = vendor
        self.clockin = clockin
        self.clockin_out = Signal(bool(0))
        self.input_frequency = int(clockin.frequency)
        self.reset = reset
        self.enable = Signal(bool(0))
        self.output_frequencies = tuple(map(int, output_frequencies))
        self.clocks = [Clock(0, f) for f in output_frequencies]
        self.clocksout = Signal(intbv(0)[number_of_outputs:])
        for ii, clk in enumerate(self.clocks):
            vars(self)['clock{:02d}'.format(ii)] = clk
        self.locked = Signal(bool(0))
