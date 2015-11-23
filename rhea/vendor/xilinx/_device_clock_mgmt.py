
from __future__ import absolute_import
from __future__ import division

from math import fmod
from fractions import gcd

from rhea.system import Reset
from .._device_clock_mgmt_prim import device_clock_mgmt_prim


def device_clock_mgmt(clkmgmt):
    
    # assign the individual clocks in th epll_intf to the 
    # clock bit-vector (interface mappings)
    number_of_outputs = len(clkmgmt.output_frequencies)

    # generate the correct polarity reset regardless of the reset
    # type attached to the interface.  If the interface does not 
    # have a reset create a state "no reset")\.  Reset syncros 
    # are handled external to this module
    reseti = Reset(0, active=1, async=True)
    reset = Reset(0, active=1, async=True)
    stuck_reset = False
    if clkmgmt.reset is None:
        stuck_reset = True
    else:
        reset = clkmgmt.reset
    clkmgmt.reset = reseti
    active = reseti.active

    @always_comb
    def beh_assign():
        for ii in range(number_of_outputs):
            clkmgmt.clocks[ii].next = clkmgmt.clocksout[ii]

        if stuck_reset:
            reseti.next = False
        elif active == 0:
            reseti.next = not reset
        else:
            reseti.next = reset

    prim_inst = device_clock_mgmt_prim(clkmgmt)
    device_clock_mgmt_prim.verilog_code = clock_mgmt_verilog_code(clkmgmt)

    return prim_inst


def mmcm_parameters(cifreq=100e6, cofreqs=[100e6, 125e6, 180e6]):
    """
    """
    search, M = True, 1
    best = [M, 10]
    
    def isint(x):
        return fmod(x, 1) == 0

    while search and M < 64:
        M = M + 1
        fb = M*cifreq
        d = [fb/cf for cf in cofreqs]
        if False in list(map(isint, d)):
            search = True
            w = sum([fmod(dd, 1) for dd in d])
            if w < best[1]:
                best = [M, w]
        else:
            search = False

    print(M)
    D = [int(round(fb/cf)) for cf in cofreqs]
    print(D)
    return M, D


def clock_mgmt_verilog_code(clkmgmt):
    """
    This uses a mix of string replacement, as documented in the myhdl
    manual the "%" is used by the converted to insert signal/variable
    names.  Locally the {} format is used to extract parameters from
    the PLL interface (`pll_intf`)
    """
    
    mult_f, divides = mmcm_parameters(clkmgmt.clockin.frequency,
                                      clkmgmt.output_frequencies)
    divide_f = divides[0]
    # Parameters
    tstr = '\n '.join([".CLKOUT{}_DIVIDE  ( {} ), ".format(ii, div)
                       for div in divices[1:]])
    clkmgmt.PARAM_output_divides = tstr
    clkmgmt.mult_f = mult_f
    clkmgmt.divide_f = divide_f

    tstr = '\n '.join([".CLKOUT{}_DUTY_CYCLE  ( 0.5 ), ".format(ii)
                       for ii in range(len(clkmgmt.clocks))])
    clkmgmt.PARAM_duty_cycle = tstr

    tstr = '\n '.join([".CLKOUT{}_DUTY_PHASE  ( 0.0 ), ".format(ii)
                       for ii in range(len(clkmgmt.clocks))])
    clkmgmt.PARAM_phase = tstr

    # Ports 
    #tstr = '\n '.join([".CLKOUT{}  ( {} ), ".format(ii)
    #                   for ii in range(len(clkmgmt.clocks))])
                   
    template = """
    wire mmcm_clkfb;
    wire mmcm_pwrdwn;
    wire [6:0] oclkwzy123qrs;

    assign mmcm_reset = 1'b0;

    MMCME2_BASE #(
      .BANDWIDTH         ( "OPTIMIZED" ),
      .CLKIN1_PERIOD     ( {input_frequency} ),
      .CLKFBOUT_MULT_F   ( {mult_f} ),
      .CLKFBOUT_PHASE    ( 0.0 ),
      .CLKOUT0_DIVIDE_F  ( {divide_f} ),
      {PARAM_output_divides}
      {PARAM_duty_cycle}
      {PARAM_phase}
      .CLKOUT4_CASCADE   ( "FALSE" ),
      .DIVCLK_DIVIDE     ( 1 ),
      .REF_JITTER        ( 0.0 ),
      .STARTUP_WAIT      ( "FALSE" ) )
    U_MMCME2_BASE_{clkmgmt_num} (
      .CLKOUT0   ( oclkwzy123qrs[0] ),
      .CLKOUT1   ( oclkwzy123qrs[1] ),
      .CLKOUT2   ( oclkwzy123qrs[2] ),
      .CLKOUT3   ( oclkwzy123qrs[3] ),
      .CLKOUT4   ( oclkwzy123qrs[4] ),
      .CLKOUT5   ( oclkwzy123qrs[5] ),
      .CLKOUT6   ( oclkwzy123qrs[6] ),
      .CLKFBOUT  ( mmcm_clkfb ),
      .CLKFBOUTB ( ),
      .CLKFBIN   ( mmcm_clkfb ),
      .LOCKED    ( $locked ),
      .CLKIN     ( $clockin ),
      .PWRDWN    ( mmcm_pwrdwn ),
      .RST       ( $reset )
    );

    assign $clocksout = oclkwzy123qrs;
    """.format(**vars(clkmgmt))

    return template