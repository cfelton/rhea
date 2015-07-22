
from myhdl import *


def m_btn_debounce(glbl, bnts, dbnts):

    cnt = Signal(intbv(0, min=0, max=33))

    # @todo finish and use m_time_strobe that checks
    #   glbl for a strober
    @always(glbl.clock.posedge)
    def rtl():
        dbnts.next = bnts

    return rtl