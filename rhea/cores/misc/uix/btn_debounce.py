
import myhdl
from myhdl import Signal, intbv, always


@myhdl.block
def button_debounce(glbl, bnts, dbnts):

    clock = glbl.clock

    # @todo finish and use m_time_strobe that checks
    #   glbl for a strober
    @always(clock.posedge)
    def beh_capture():
        dbnts.next = bnts

    return beh_capture
