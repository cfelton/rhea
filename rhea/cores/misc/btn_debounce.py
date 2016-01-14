
from myhdl import Signal, intbv, always


def button_debounce(glbl, bnts, dbnts):

    clock = glbl.clock

    # @todo finish and use m_time_strobe that checks
    #   glbl for a strober
    @always(clock.posedge)
    def rtl():
        dbnts.next = bnts

    return rtl
