
from myhdl import always_comb


def assign(a, b):
    """ a = b """

    @always_comb
    def assign():
        a.next = b

    return assign,
