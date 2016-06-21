

import myhdl
from myhdl import Signal, intbv, always_seq

from . import HDMIExtInterface


@myhdl.block
def hdmi_xcvr(glbl, vidstream, hdmiext):
    """
    """
    assert isinstance(hdmiext, HDMIExtInterface)

    clock, reset = glbl.clock, glbl.reset
    go = Signal(bool(0))

    @always_seq(clock.posedge, reset=reset)
    def beh():
        if glbl.enable:
            go.next = True
        else:
            go.next = False

    return myhdl.instances()
