
from __future__ import absolute_import

import myhdl
from myhdl import always_comb

from rhea.system import Reset
from ..device_clock_mgmt_prim import device_clock_mgmt_prim


@myhdl.block
def device_clock_mgmt(clkmgmt):

    # assign the individual clocks in the pll_intf to the
    # clock bit-vector (interface mappings)
    number_of_outputs = len(clkmgmt.output_frequencies)

    # generate the correct polarity reset regardless of the reset
    # type attached to the interface.  If the interface does not
    # have a reset create a static "no reset".  Reset syncros
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

    # attach the intended Verilog code to the block, the
    # Verilog code will be inserted instead of device_clock_mgmt_prim
    # converted.        
    device_clock_mgmt_prim.verilog_code = clock_mgmt_verilog_code(clkmgmt)
    # device_clock_mgmt_prim.vhdl_code = clock_mgmt_vhdl_code(clkmgmt)
    prim_inst = device_clock_mgmt_prim(clkmgmt)

    return prim_inst, beh_assign


def clock_mgmt_verilog_code(clkmgmt):
    """
    This uses a mix of string replacement, as documented in the myhdl
    manual the "%" is used by the converted to insert signal/variable
    names.  Locally the {} format is used to extract parameters from
    the PLL interface (`pll_intf`)
    """

    # Parameters
    # @todo: determine if the output frequencies are reasonable ...
    tstr = '\n  '.join([".CLK{ii}_OUTPUT_FREQUNECY( {of} ),".format(ii=ii, of=of)
                        for ii, of in enumerate(clkmgmt.output_frequencies)])
    clkmgmt.PARAM_output_frequencies = tstr

    # Ports
    tstr = '\n  '.join([".c{ii}( $clocksout [{ii}] ),".format(ii=ii)
                        for ii in range(len(clkmgmt.clocks))])
    clkmgmt.PORT_clocksout = tstr


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
    U_ATLPLL_{clkmgmt_num}
      (.inclk      (  $clockin    ),
       .areset     (  $reset      ),
       .pllena     (  $enable     ),
       .clk        (  $clocksout  ),
       .locked     (  $locked     ) );
    """.format(**vars(clkmgmt))

    return template