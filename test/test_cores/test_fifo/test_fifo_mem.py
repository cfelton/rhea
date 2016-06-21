
from random import randint

import pytest

import myhdl
from myhdl import Signal, ResetSignal, intbv, modbv, always_seq
from myhdl import instance, delay, StopSimulation
from myhdl.conversion import analyze, verify

from rhea.system import Signals
from rhea.cores.fifo.fifo_mem import fifo_mem


def test_fifo_mem_convert():
    clock = Signal(bool(0))
    write, read = Signal(bool(0)), Signal(bool(0))
    write_data, read_data = Signal(intbv(0)[8:0]), Signal(intbv(0)[8:0])
    write_addr, read_addr = Signal(intbv(0)[8:0]), Signal(intbv(0)[8:0])
    wad = Signal(intbv(0)[8:0])

    inst = fifo_mem(clock, write, write_data, write_addr,
                    clock, read, read_data, read_addr, wad)
    inst.convert(hdl='Verilog', directory=None)


def test_fifo_mem_analyze():
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
def bench_fifo_mem_rand():
    nloops = 100
    w = width = 8
    wmax = 2 ** width

    # random data and addresses for test
    rand_data = tuple([randint(0, wmax - 1) for _ in range(nloops)])
    rand_addr = tuple([randint(0, wmax - 1) for _ in range(nloops)])

    clock, write, read = Signals(bool(0), 3)
    write_data, write_addr, read_data, read_addr = Signals(intbv(0)[w:0], 4)
    wad = Signal(write_addr.val)

    tbdut = fifo_mem(clock, write, write_data, write_addr,
                     clock, read, read_data, read_addr, wad)

    @instance
    def tbclkw():
        clock.next = False
        while True:
            yield delay(5)
            clock.next = not clock

    @instance
    def tbstim():
        print("start sim")
        write.next = False
        write_data.next = 0
        write_addr.next = 0
        read.next = False
        read_addr.next = 0

        print("delay some")
        yield delay(10)
        for ii in range(5):
            yield clock.posedge

        for ii in range(wmax):
            write.next = True
            write_data.next = 0
            yield clock.posedge
        write.next = False

        print("write loop")
        for ii in range(nloops):
            write.next = True
            write_data.next = rand_data[ii]
            write_addr.next = rand_addr[ii]
            read_addr.next = wad
            yield clock.posedge
            write.next = False
            for jj in range(3):
                yield clock.posedge
            print("%d %d %d %d" % (
                write_addr, write_data, read_addr, read_data))
        write.next = False

        print("read loop")
        for ii in range(nloops):
            write_data.next = rand_data[ii]
            write_addr.next = rand_addr[ii]
            read_addr.next = rand_addr[ii]
            yield clock.posedge
            print("%d %d %d %d" % (
                write_addr, write_data, read_addr, read_data))
        write.next = False
        yield clock.posedge

        print("end sim")
        raise StopSimulation

    return myhdl.instances()


def test_fifo_mem_verify_verilog():
    verify.simulator = 'iverilog'
    inst = bench_fifo_mem_rand()
    assert inst.verify_convert() == 0


# @pytest.mark.skip(reason="missing ghdl in travis")
# def test_fifo_mem_verify_vhdl():
#     verify.simulator = 'ghdl'
#     inst = bench_fifo_mem_rand()
#     assert inst.verify_convert() == 0


@myhdl.block
def bench_fifo_mem_inc():
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
        write_addr.next = 0
        read_addr.next = 0
        print("start simulation")
        for ii in range(5):
            yield clock.posedge
        print("write data")
        for ii in range(16):
            write.next = True
            write_data.next = ii
            write_addr.next = ii
            yield clock.posedge
            print("%d %d %d" % (ii, write_addr, write_data,))
        write.next = False
        yield clock.posedge
        yield clock.posedge
        print("read data")
        for ii in range(16):
            read.next = True
            read_addr.next = ii
            yield clock.posedge
            print("%d %d %d" % (ii, read_addr, read_data,))
            assert read_data == ii
        print("end simulation")
        raise StopSimulation

    return myhdl.instances()  # tbdut, tbclk, tbstim


def test_verify_bench_fifo_mem_inc():
    verify.simulator = 'iverilog'
    inst = bench_fifo_mem_inc()
    assert inst.verify_convert() == 0


@myhdl.block
def fifo_mem_wrapper(clock, reset, datain, div, dataout, dorq):
    write_addr = Signal(modbv(0)[8:0])
    read_addr = Signal(modbv(0)[8:0])
    wad = Signal(intbv(0)[8:0])

    mem_inst = fifo_mem(clock, div, datain, write_addr,
                        clock, dorq, dataout, read_addr, wad)

    @always_seq(clock.posedge, reset=reset)
    def beh_addr():
        if div:
            write_addr.next = write_addr + 1

        if dorq:
            read_addr.next = read_addr + 1

    return myhdl.instances()


@myhdl.block
def bench_fifo_mem_wrapper():
    clock = Signal(bool(0))
    reset = ResetSignal(0, active=0, async=True)
    div, dorq = Signal(bool(0)), Signal(bool(0))
    datain, dataout = Signal(intbv(0)[8:0]), Signal(intbv(0)[8:0])

    tbdut = fifo_mem_wrapper(clock, reset, datain, div, dataout, dorq)

    @instance
    def tbclk():
        clock.next = False
        while True:
            yield delay(5)
            clock.next = not clock

    @instance
    def tbstim():
        reset.next = reset.active
        yield delay(20)
        reset.next = not reset.active
        yield clock.posedge

        print("start simulation")
        print("write data")
        for ii in range(16):
            div.next = True
            datain.next = ii
            yield clock.posedge
            print("%d %d" % (ii, datain,))
        div.next = False
        yield clock.posedge
        print("read data")
        for ii in range(16):
            dorq.next = True
            # assert read_data == ii
            yield clock.posedge
            print("%d %d" % (ii, dataout,))
        print("end simulation")
        raise StopSimulation

    return tbdut, tbclk, tbstim


def test_verify_bench_fifo_mem_wrapper():
    verify.simulator = 'iverilog'
    inst = bench_fifo_mem_wrapper()
    assert inst.verify_convert() == 0
