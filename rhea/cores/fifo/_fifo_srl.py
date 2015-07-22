

from myhdl import *

def m_fifo_srl(clock, D, ce, addr, Q, Qn=None):
    """
    Infer a shift-register-LUT without explicilty instatiating a device
    specific primitive.  This is typical in most FPGAs and works for std
    cell as well (nothing special happens in std cell).

    Information on Xilinx SRL:
    http://www.xilinx.com/support/documentation/application_notes/xapp465.pdf
    http://www.xilinx.com/support/documentation/sw_manuals/xilinx14_5/xst_v6s6.pdf, page 154
    """
    W = 16
    assert len(addr) == 4, "this is fixed to a length of 16"
    srl = Signal(intbv(0)[W:])

    @always(clock.posedge)
    def rtl():
        if ce:
            srl.next = concat(srl[W-2:0], D)
            #srl.next[0] = D
            #slr.next[W-1:1] = slr[W-2:0]

    @always_comb
    def rtl_out():
        Q.next = srl[addr]
        
    if Qn is not None:
        @always_comb
        def rtl_outn():
            Qn.next = srl[W-1]

        g = (rtl, rtl_out, rtl_outn)
    else:
        g = (rtl, rtl_out,)

    return g

    