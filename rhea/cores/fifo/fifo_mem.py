#
# Copyright (c) 2006-2014 Christopher L. Felton
#

from math import ceil, log
from myhdl import Signal, intbv, always_comb, always


def fifo_mem_generic(wclk, wr, din, addr_w,
                     rclk, dout, addr_r,
                     mem_size=9):
    """ Memory module used by FIFOs
    Ports
    =====

    Parameters
    ==========
      mem_size: number of item entries in the memory
    """

    Asz = int(ceil(log(mem_size, 2)))
    assert len(din) == len(dout)
    Dsz = len(din)

    mem = [Signal(intbv(0)[Dsz:]) for ii in range(2**Asz)]
    _addr_w = Signal(intbv(0)[Asz:])
    _din = Signal(intbv(0)[Dsz:])
    _dout = Signal(intbv(0)[Dsz:])
    _wr = Signal(bool(0))

    @always_comb
    def rtl_dout():
        dout.next = _dout

    @always(rclk.posedge)
    def rtl_rd():
        _dout.next = mem[int(addr_r)]

    @always(wclk.posedge)
    def rtl_wr():
        _wr.next = wr
        _addr_w.next = addr_w
        _din.next = din

    @always(wclk.posedge)
    def rtl_mem():
        if _wr:
            mem[int(_addr_w)].next = _din

    return rtl_dout, rtl_rd, rtl_wr, rtl_mem
