

import myhdl
from myhdl import Signal, intbv, always, always_comb, concat


@myhdl.block
def fifo_srl(clock, din, ce, addr, dout, dlast=None):
    """
    Infer a shift-register-LUT without explicitly instantiating a device
    specific primitive.  This is typical in most FPGAs and works for std
    cell as well (nothing special happens in std cell).

    Information on Xilinx SRL:
    http://www.xilinx.com/support/documentation/application_notes/xapp465.pdf
    http://www.xilinx.com/support/documentation/sw_manuals/xilinx14_5/xst_v6s6.pdf, page 154
    """
    w = 16
    assert len(addr) == 4, "this is fixed to a length of 16"
    srl = Signal(intbv(0)[w:])

    @always(clock.posedge)
    def beh_input():
        if ce:
            srl.next = concat(srl[w-2:0], din)

    @always_comb
    def beh_out():
        dout.next = srl[addr]
        
    if dlast is not None:
        @always_comb
        def beh_outn():
            dlast.next = srl[w-1]

        g = (beh_input, beh_out, beh_outn)
    else:
        g = (beh_input, beh_out,)

    return g
