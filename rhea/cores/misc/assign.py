
import myhdl
from myhdl import Signal, SignalType, always_comb


@myhdl.block
def assign(a, b):
    """ assign a = b
    """

    if isinstance(b, SignalType):
        @always_comb
        def beh_assign():
            a.next = b
    else:
        # this is a work around for preserving constant assigns
        keep = Signal(True)
        keep.driven = "wire"

        @always_comb
        def beh_assign():
            a.next = b if keep else b

    return beh_assign
