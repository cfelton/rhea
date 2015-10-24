
from __future__ import absolute_import

from myhdl import always_comb

from rhea.system import Reset
from .._device_pll_prim import device_pll_prim


def device_pll(pll_intf):

    # assign the individual clocks in the pll_intf to the
    # to clock bit-vector (interface mappings)
    number_of_outputs = len(pll_intf.output_frequencies)
    
    # generate the correct polarity reset regardless of the reset
    # type attached to the interface.  If the interface does not 
    # have a reset create a static "no reset).  Reset syncros 
    # are handled external to this module
    reseti = Reset(0, active=1, async=True)
    reset = Reset(0, active=1, async=True)
    stuck_reset = False
    if pll_intf.reset is None:
        stuck_reset = True
    else:
        reset = pll_intf.reset
    pll_intf.reset = reseti
    active = reseti.active

    @always_comb
    def beh_assign():
        for ii in range(number_of_outputs):
            pll_intf.clocks[ii].next = pll_intf.clocksout[ii]

        if stuck_reset:
            reseti.next = False
        elif active == 0:
            reseti.next = not reset
        else:
            reseti.next = reset

    # get the Verilog primitive instance
    prim_inst = device_pll_prim(pll_intf)
    device_pll_prim.verilog_code = pll_verilog_code(pll_intf)
    # device_pll_prin.vhdl_code = pll_vhdl_code(pll_intf)

    return prim_inst, beh_assign


def pll_verilog_code(pll_intf):
    """
    This uses a mix of string replacement, as documented in the myhdl
    manual the "%" is used by the converted to insert signal/variable
    names.  Locally the {} format is used to extract parameters from
    the PLL interface (`pll_intf`)
    """

    # Parameters
    # @todo: determine if the output frequencies are reasonable ...
    tstr = '\n  '.join([".CLK{ii}_OUTPUT_FREQUNECY( {of} ),".format(ii=ii, of=of)
                        for ii, of in enumerate(pll_intf.output_frequencies)])
    pll_intf.PARAM_output_frequencies = tstr

    # Ports
    tstr = '\n  '.join([".c{ii}( $clocksout [{ii}] ),".format(ii=ii)
                        for ii in range(len(pll_intf.clocks))])
    pll_intf.PORT_clocksout = tstr


    # custom clocks out ports and parameters, the string template
    # $name will be replaced by the myhdl conversion.  These reference
    # the signals in the `vendor.device_pll_prim` module.  The {} will
    # be inserted by the string format, these are parameters etc.
    template = """
    altpll
      #( .OPERATION_MODE("NORMAL"),  /// @todo: verify this mode
         .INCLK0_INPUT_FREQUENCY( {input_frequency}  ),
         {PARAM_output_frequencies}
         .PORT_LOCKED( "PORT_USED") )
    U_ATLPLL_{pll_num}
      (.inclk      (  $clockin    ),
       .areset     (  $reset      ),
       .pllena     (  $enable     ),
       .clk        (  $clocksout  ),
       .locked     (  $locked     ) );
    """.format(**vars(pll_intf))

    return template
