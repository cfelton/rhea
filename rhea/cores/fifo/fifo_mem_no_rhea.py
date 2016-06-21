import myhdl
from myhdl import Signal, modbv, intbv, always_comb, always
from myhdl import instance, delay, StopSimulation
from myhdl.conversion import analyze, verify


@myhdl.block
def fifo_mem(clock_w, write, write_data, write_addr,
             clock_r, read, read_data, read_addr, write_addr_delayed):
    """ Memory module used by FIFOs
    This block describes the behavior of a dual-port memory with 
    registered inputs and outputs.

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

    Parameters:
        mem_size (int): number of item entries in the memory.
    """
    
    assert len(write_addr) == len(read_addr)
    addrsize = len(write_addr)
    memsize = 2**len(write_addr)
    assert len(write_data) == len(read_data)
    datasize = len(write_data)

    # create the list-of-signals to represent the memory array
    memarray = [Signal(intbv(0)[datasize:0]) for _ in range(memsize)]

    addr_w = Signal(modbv(0)[addrsize:0])
    addr_wd = Signal(modbv(0)[addrsize:0])
    addr_r = Signal(modbv(0)[addrsize:0])
    din = Signal(intbv(0)[datasize:])
    dout = Signal(intbv(0)[datasize:])
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

    return (beh_write_capture, beh_mem_write, beh_write_address_delayed,
            beh_read_next, beh_mem_read,)


def test_conversion():
    clock = Signal(bool(0))
    write, read = Signal(bool(0)), Signal(bool(0))
    write_data, read_data = Signal(intbv(0)[8:0]), Signal(intbv(0)[8:0])
    write_addr, read_addr = Signal(intbv(0)[8:0]), Signal(intbv(0)[8:0])
    wad = Signal(intbv(0)[8:0])

    inst = fifo_mem(clock, write, write_data, write_addr,
    clock, read, read_data, read_addr, wad)

    analyze.simulator = 'iverilog'
    assert inst.analyze_convert() == 0


@myhdl.block
def bench_convertible():
    clock = Signal(bool(0))
    write, read = Signal(bool(0)), Signal(bool(0))
    write_data, read_data = Signal(intbv(0)[8:0]), Signal(intbv(0)[8:0])
    write_addr, read_addr = Signal(intbv(0)[8:0]), Signal(intbv(0)[8:0])
    wad = Signal(intbv(0)[8:0])

    tbdut = fifo_mem(clock, write, write_data, write_addr,
                      clock, read, read_data, read_addr, wad)

    @instance
    def tbclk():
        clock.next = False
        while True:
            yield delay(5)
            clock.next = not clock

    @instance
    def tbstim():
        print("start simulation")
        for ii in range(16):
            write.next = True
            write_data.next = ii
            write_addr.next = ii
            yield clock.posedge
            print("%d %d %d" % (ii, write_addr, write_data,))
        write.next = False
        yield clock.posedge
        for ii in range(16):
            read.next = True
            read_addr.next = ii
            # assert read_data == ii
            yield clock.posedge
            print("%d %d %d" % (ii, read_addr, read_data,))
        print("end simulation")
        raise StopSimulation

    return tbdut, tbclk, tbstim


def test_verify_conversion():
    verify.simulator = 'iverilog'
    inst = bench_convertible()
    assert inst.verify_convert() == 0


if __name__ == '__main__':
    test_conversion()
    test_verify_conversion()
