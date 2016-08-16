
from __future__ import absolute_import, division

from math import fmod
from fractions import gcd

import myhdl
from myhdl import always_comb

from rhea.system import Reset
from ..device_clock_mgmt_prim import device_clock_mgmt_prim


@myhdl.block
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

    # Prevent phantom conversion warnings about these signals not
    # being driven or read.  (They escape via clock_management_verilog_code)
    clkmgmt.clockin.read = True
    reseti.read = True
    reset.read = True
    reset.driven = True

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

    # attach the intended Verilog code to the block, the
    # Verilog code will be inserted instead of device_clock_mgmt_prim
    # converted.        
    device_clock_mgmt_prim.verilog_code = clock_mgmt_verilog_code(clkmgmt)
    prim_inst = device_clock_mgmt_prim(clkmgmt)

    return prim_inst, beh_assign


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
        # @todo: need to add "D", if geater use a
        # @todo: reasonable "D" value
        vco_freq_mhz = fb/1e6
        if vco_freq_mhz < 600 or vco_freq_mhz > 1250:
            continue
            
        d = [fb/cf for cf in cofreqs]
        if False in list(map(isint, d)):
            search = True
            w = sum([fmod(dd, 1) for dd in d])
            if w < best[1]:
                best = [M, w]
        else:
            search = False

    odiv = [int(round(fb/cf)) for cf in cofreqs]
    return M, odiv


def clock_mgmt_verilog_code(clkmgmt):
    """
    This uses a mix of string replacement, as documented in the myhdl
    manual the "%" is used by the converted to insert signal/variable
    names.  Locally the {} format is used to extract parameters from
    the PLL interface (`pll_intf`)
    """

    # input clock period in ns
    clkmgmt.input_period = 1e9/clkmgmt.clockin.frequency
    
    mult_f, divides = mmcm_parameters(clkmgmt.clockin.frequency,
                                      clkmgmt.output_frequencies)
    divide_f = divides[0]
    # Parameters
    tstr = '\n '.join(["{}.CLKOUT{}_DIVIDE  ( {} ), ".format(' '*6, ii, div)
                       for ii, div in enumerate(divides) if ii > 0 ])
    clkmgmt.PARAM_output_divides = tstr
    clkmgmt.mult_f = mult_f
    clkmgmt.divide_f = divide_f
    
    tstr = '\n '.join(["{}.CLKOUT{}_DUTY_CYCLE  ( 0.5 ), ".format(' '*6, ii)
                       for ii in range(len(clkmgmt.clocks))])
    clkmgmt.PARAM_duty_cycle = tstr

    tstr = '\n '.join(["{}.CLKOUT{}_PHASE  ( 0.0 ), ".format(' '*6, ii)
                       for ii in range(len(clkmgmt.clocks))])
    clkmgmt.PARAM_phase = tstr

    # Ports 
    #tstr = '\n '.join([".CLKOUT{}  ( {} ), ".format(ii)
    #                   for ii in range(len(clkmgmt.clocks))])
                   
    template = """
    wire mmcm_clkfb;
    wire mmcm_pwrdwn;
    wire [6:0] oclkwzy123qrs;

    assign mmcm_pwrdwn = 1'b0;
    assign mmcm_reset = 1'b0;

    MMCME2_BASE #(
      .BANDWIDTH         ( "OPTIMIZED" ),
      .CLKIN1_PERIOD     ( {input_period:.1f} ),
      .CLKFBOUT_MULT_F   ( {mult_f} ),
      .CLKFBOUT_PHASE    ( 0.0 ),
      .CLKOUT0_DIVIDE_F  ( {divide_f} ),
{PARAM_output_divides}
{PARAM_duty_cycle}
{PARAM_phase}
      .CLKOUT4_CASCADE   ( "FALSE" ),
      .DIVCLK_DIVIDE     ( 1 ),
      .REF_JITTER1       ( 0.0 ),
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
      .CLKIN1    ( $clockin ),
      .PWRDWN    ( mmcm_pwrdwn ),
      .RST       ( $reset )
    );

    assign $clocksout = oclkwzy123qrs;
    """.format(**vars(clkmgmt))

    return template
