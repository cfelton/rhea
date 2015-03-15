
from myhdl import *

def m_assign(a, b):
    """ a = b """
    @always_comb
    def assing():
        a.next = b
    return assign