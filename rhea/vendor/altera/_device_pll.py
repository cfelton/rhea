
from __future__ import absolute_import

from myhdl import always_comb
from .._device_pll_prim import device_pll_prim


def device_pll(pll_intf):

    # get the Verilog primitive instance
    prim_inst = device_pll_prim(pll_intf)
    device_pll_prim.verilog_code = pll_verilog_code(pll_intf)
    # device_pll_prin.vhdl_code = pll_vhdl_code(pll_intf)

    # assign the individual clocks in the pll_intf to the
    # to clock bit-vector (interface mappings)
    number_of_outputs = len(pll_intf.output_frequencies)

    @always_comb
    def beh_assign():
        for ii in range(number_of_outputs):
            pll_intf.clocks[ii].next = pll_intf.clocksout[ii]

    return prim_inst, beh_assign


def pll_verilog_code(pll_intf):
    """
    This uses a mix of string replacement, as documented in the myhdl
    manual the "%" is used by the converted to insert signal/variable
    names.  Locally the {} format is used to extract parameters from
    the PLL interface (`pll_intf`)
    """
    # @todo: determine if the output frequencies are reasonable ...
    tstr = '\n  '.join([".CLK{ii}_OUTPUT_FREQUNECY( {of} ),".format(ii=ii, of=of)
                        for ii, of in enumerate(pll_intf.output_frequencies)])
    pll_intf.PARAM_output_frequencies = tstr

    # custom clocks out ports and parameters, the string template
    # $name will be replaced by the myhdl conversion.  These reference
    # the signals in the `vendor.device_pll_prim` module.  The {} will
    # be inserted by the string format, these are parameters etc.
    template = """
    altpll
      #( .OPERATION_MODE("NORMAL"),  /// @todo: verify this mode
         .INCLK0_INPUT_FREQUENCY( "{input_frequency} MHz"  ),
         {PARAM_output_frequencies}
         .PORT_LOCKED( "PORT_USED") )
    U_ATLPLL_{pll_num}
      (.inclk      (  $clockin    ),
       .pllena     (  $enable     ),
       .locked     (  $locked     ),
       .c          (  $clocksout  ) );
    """.format(**vars(pll_intf))

    return template
