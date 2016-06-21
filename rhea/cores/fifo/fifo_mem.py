#
# Copyright (c) 2006-2014 Christopher L. Felton
# See the licence file in the top directory
#


import myhdl
from myhdl import Signal, modbv, intbv
from myhdl import always_comb, always
from rhea.system import Signals


@myhdl.block
def fifo_mem(clock_w, write, write_data, write_addr,
             clock_r, read, read_data, read_addr, write_addr_delayed):
    """ Memory module used by FIFOs

    The write data takes two `clock_w` clock cycles to be latched
    into the memory array and one `clock_r` clock cycle to be latched
    into `read_data`.

    Arguments:
       clock_w: write clock
       write: write enable
       write_data: write data bus
       write_addr: write address bus
       clock_r: read clock
       read: read strobe, loads the next address into the output reg
       read_data: read data bus
       read_addr: read address bus
       write_addr_delayed: the write data takes multiple clock cycles
           before it is available in the memory (pipelines before and
           and after the memory array).  This is a delayed version of
           the write_addr that matches the write_data delay.

    The memory size is determine from the address width.
    """
    
    assert len(write_addr) == len(read_addr)
    addrsize = len(write_addr)
    memsize = 2**len(write_addr)
    assert len(write_data) == len(read_data)
    datasize = len(write_data)
    # print("FIFO memory size {}, data width {}, address width {}".format(
    #     memsize, datasize, addrsize
    # ))

    # create the list-of-signals to represent the memory array
    memarray = Signals(intbv(0)[datasize:0], memsize)

    addr_w, addr_wd, addr_r = Signals(modbv(0)[addrsize:], 3)
    din, dout = Signals(intbv(0)[datasize:], 2)
    wr = Signal(bool(0))

    @always(clock_w.posedge)
    def beh_write_capture():
        # inputs are registered
        wr.next = write
        addr_w.next = write_addr
        din.next = write_data

    @always(clock_w.posedge)
    def beh_mem_write():
        if wr:
            memarray[addr_w].next = din

    @always(clock_r.posedge)
    def beh_write_address_delayed():
        addr_wd.next = write_addr
        write_addr_delayed.next = addr_wd

    @always_comb
    def beh_read_next():
        # output is registered, this block (fifo_mem) is used as
        # memory for various FIFOs, on read assume incrementing
        # to the next address, get the next address.
        if read:
            addr_r.next = read_addr+1
        else:
            addr_r.next = read_addr

    @always(clock_r.posedge)
    def beh_mem_read():
        dout.next = memarray[addr_r]

    @always_comb
    def beh_dataout():
        read_data.next = dout

    return myhdl.instances()
