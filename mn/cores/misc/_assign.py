
from myhdl import *

def m_assign(a, b):
    """ a = b """
    @always_comb
    def assign():
        a.next = b
    return assign