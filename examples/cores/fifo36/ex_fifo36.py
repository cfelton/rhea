
"""
This example takes a different 
"""

from argparse import Namespace

from myhdl import *

from rhea.system import FIFOBus
from rhea.cores.fifo import fifo_async
from rhea.cores.fifo import fifo_fast


def fifo_2clock_cascade(
    wclk,       # in:  write side clock
    datain,     # in:  write data
    src_rdy_i,  # in:  
    dst_rdy_o,  # out: 
    space,      # out: how many can be written
    
    rclk,       # in:  read side clock
    dataout,    # out: read data
    src_rdy_o,  # out: 
    dst_rdy_i,  # in:  
    occupied,   # out: number in the fifo

    reset,      # in:  system reset
):


    wr = Signal(bool(0))
    rd = Signal(bool(0))
    dataout_d = Signal(intbv(0, min=dataout.min, max=dataout.max))

    args = Namespace(width=36, size=128, name='fifo_2clock_cascade')
    fbus = FIFOBus(size=args.size, width=args.width)
    # need to update the fbus refernces to reference the Signals in
    # the moudule port list (function arguments).
    fbus.write = wr
    fbus.write_data = datain
    fbus.read = rd
    fbus.read_data = dataout_d

    @always_comb
    def rtl_assign1():
        wr.next = src_rdy_i & dst_rdy_o
        rd.next = dst_rdy_i & src_rdy_o

    @always_comb
    def rtl_assign2():
        dst_rdy_o.next = not fbus.full
        src_rdy_o.next = not fbus.empty

    # the original was a chain:
    #    m_fifo_fast  (16)
    #    m_fifo_async (??)
    #    m_fifo_fast  (16)
    gfifo = fifo_async(reset, wclk, rclk, fbus)
    # @todo: calculate space and occupied based on fbus.count
        
    # @todo: the output is delayed two clock from the "read" strobe
    #   the m_fifo_async only has a delta of one (read valid strobe
    #   aligns with valid data).  Need to delay the data one more
    #   clock cycle???
    
    @always(rclk.posedge)
    def rtl_delay():
        dataout.next = dataout_d

    return rtl_assign1, rtl_assign2, gfifo, rtl_delay


def fifo_short(clock, reset, clear,
               datain, src_rdy_i, dst_rdy_o,
               dataout, src_rdy_o, dst_rdy_i):

    wr = Signal(bool(0))
    rd = Signal(bool(0))

    args = Namespace(width=36, size=16, name='fifo_2clock_cascade')
    fbus = FIFOBus(size=args.size, width=args.width)
    # need to update the fbus refernces to reference the Signals in
    # the module port list (function arguments).
    fbus.write = wr
    fbus.write_data = datain
    fbus.read = rd
    fbus.read_data = dataout

    @always_comb
    def rtl_assign1():
        wr.next = src_rdy_i & dst_rdy_o
        rd.next = dst_rdy_i & src_rdy_o

    @always_comb
    def rtl_assign2():
        dst_rdy_o.next = not fbus.full
        src_rdy_o.next = not fbus.empty

    gfifo = fifo_fast(reset, clock, fbus)

    return rtl_assign1, rtl_assign2, gfifo
    

def convert(args=None):
    wclk = Signal(bool(0))
    datain = Signal(intbv(0)[36:])
    src_rdy_i = Signal(bool(0))
    dst_rdy_o = Signal(bool(0))
    space = Signal(intbv(0)[16:])
    
    rclk = Signal(bool(0))
    dataout = Signal(intbv(0)[36:])
    src_rdy_o = Signal(bool(0))
    dst_rdy_i = Signal(bool(0))
    occupied = Signal(intbv(0)[16:])

    reset = ResetSignal(0, active=1, async=True)

    toVerilog(fifo_2clock_cascade,
              wclk, datain, src_rdy_i, dst_rdy_o, space,
              rclk, dataout, src_rdy_o, dst_rdy_i, occupied,
              reset)

    clock = Signal(bool(0))
    clear = Signal(bool(0))
    toVerilog(fifo_short,
              clock, reset, clear,
              datain, src_rdy_i, dst_rdy_o,
              dataout, src_rdy_o, dst_rdy_i)


if __name__ == '__main__':
    convert()