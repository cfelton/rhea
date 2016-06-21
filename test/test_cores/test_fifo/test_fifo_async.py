#
# Copyright (c) 2014 Christopher L. Felton
# See the licence file in the top directory
#

from __future__ import division, print_function

from argparse import Namespace

import myhdl
from myhdl import (Signal, ResetSignal, intbv, modbv, delay, instance,
                   always, always_comb, StopSimulation)
from myhdl.conversion import verify

from rhea.system import Clock, FIFOBus, Global, Signals
from rhea.cores.fifo import fifo_async

from rhea.utils.test import run_testbench


@myhdl.block
def procuder_consumer(clock_write, clock_read, fbus, start):
    # FIFO writer and reader
    _wr = Signal(bool(0))
    w = len(fbus.write_data)

    @instance
    def tb_always_wr():
        was_full = False
        wrd = modbv(0)[w:]
        while True:
            if start:
                break
            yield clock_write.posedge

        while True:
            yield clock_write.posedge
            if not fbus.full and was_full:
                was_full = False
                for _ in range(17):
                    yield clock_write.posedge
            elif not fbus.full:
                fbus.write_data.next = wrd
                _wr.next = True
                yield delay(1)
                if not fbus.full:
                    wrd[:] += 1
            else:
                _wr.next = False
                was_full = True

    @always_comb
    def tb_always_wr_gate():
        fbus.write.next = _wr and not fbus.full

    @instance
    def tb_always_rd():
        rdd = modbv(0)[w:]
        while True:
            if start:
                break
            yield clock_write.posedge

        while True:
            try:
                yield clock_read.posedge
                if not fbus.empty:
                    fbus.read.next = True
                else:
                    fbus.read.next = False

                if fbus.read_valid:
                    tmp = fbus.read_data
                    assert tmp == rdd, " %d != %d " % (tmp, rdd)
                    rdd[:] += 1
            except AssertionError as err:
                for _ in range(10):
                    yield clock_read.posedge
                raise err

    return myhdl.instances()


def test_async_fifo(args=None):
    """ verify the asynchronous FIFO    
    """
    if args is None:
        args = Namespace(width=8, size=16, name='test')
    
    reset = ResetSignal(0, active=1, async=True)
    wclk = Clock(0, frequency=22e6)
    rclk = Clock(0, frequency=50e6)
    fbus = FIFOBus(width=args.width)
    start = Signal(bool(0))

    @myhdl.block
    def bench_async_fifo():

        tbclkw = wclk.gen()
        tbclkr = rclk.gen()
        tbdut = fifo_async(wclk, rclk, fbus, reset)
        tbpr = procuder_consumer(wclk, rclk, fbus, start)
                
        @instance
        def tbstim():
            print("start test 1")
            fbus.write_data.next = 0xFE
            reset.next = reset.active
            yield delay(3*33)
            reset.next = not reset.active

            # reset is delayed by at least two
            for ii in range(5):
                yield wclk.posedge
        
            # test normal cases
            for num_bytes in range(1, args.size+1):
        
                # Write some byte
                for ii in range(num_bytes):
                    yield wclk.posedge
                    fbus.write_data.next = ii
                    fbus.write.next  = True
                    
                yield wclk.posedge
                fbus.write.next = False
        
                # If 16 bytes written make sure FIFO is full
                yield wclk.posedge
                if num_bytes == args.size:
                    assert fbus.full, "FIFO should be full!"
        
                while fbus.empty:
                    yield rclk.posedge
                    
                fbus.read.next = True
                yield rclk.posedge
                for ii in range(num_bytes):
                    yield rclk.posedge
                    fbus.read.next = True
                    assert fbus.read_valid
                    assert fbus.read_data == ii, "rdata %x ii %x " % (fbus.read_data, ii)
        
                yield rclk.posedge
                fbus.read.next = False
                yield rclk.posedge
                assert fbus.empty

            raise StopSimulation
        
        return myhdl.instances()


def test_(args=None):

    if args is None:
        args = Namespace(width=8, size=16, name='test')

    reset = ResetSignal(0, active=1, async=True)
    wclk = Clock(0, frequency=22e6)
    rclk = Clock(0, frequency=50e6)
    fbus = FIFOBus(width=args.width)
    start = Signal(bool(0))

    @myhdl.block
    def bench_():
        tbclkw = wclk.gen()
        tbclkr = rclk.gen()
        tbdut = fifo_async(wclk, rclk, fbus, reset)
        tbpr = procuder_consumer(wclk, rclk, fbus, start)

        @instance
        def tbstim():
            print("start test 2")
            fbus.write_data.next = 0xFE
            reset.next = reset.active
            yield delay(3*33)
            reset.next = not reset.active

            yield delay(44)
            start.next = True

            for ii in range(2048):
                yield delay(100)

            raise StopSimulation

        return myhdl.instances()

    run_testbench(bench_)


@myhdl.block
def bench_conversion_fifo_async():
    args = Namespace(width=8, size=32, fifosize=64, name='test')

    clock_write, clock_read = Signals(bool(0), 2)
    reset = ResetSignal(0, active=1, async=False)

    fbus = FIFOBus(width=args.width)
    fifosize = args.fifosize
    tbdut = fifo_async(clock_write, clock_read, fbus, reset, size=fifosize)

    @instance
    def tbclkr():
        clock_read.next = False
        while True:
            yield delay(5)
            clock_read.next = not clock_read

    @instance
    def tbclkw():
        clock_write.next = False
        while True:
            yield delay(5)
            clock_write.next = not clock_write

    @instance
    def tbstim():
        print("start simulation")
        fbus.write.next = False
        fbus.write_data.next = 0
        fbus.read.next = False
        fbus.clear.next = False

        print("reset")
        reset.next = reset.active
        yield delay(10)
        reset.next = not reset.active
        yield delay(10)

        print("some clock cycles")
        for ii in range(10):
            yield clock_write.posedge

        print("some writes")
        for ii in range(fifosize):
            fbus.write.next = True
            fbus.write_data.next = ii
            yield clock_write.posedge
        fbus.write.next = False
        yield clock_write.posedge

        for ii in range(fifosize):
            fbus.read.next = True
            yield clock_read.posedge
            print("%d %d %d %d" % (
                fbus.write, fbus.write_data, fbus.read, fbus.read_data,))
        fbus.read.next = False

        print("end simulation")
        raise StopSimulation

    return myhdl.instances()


def test_fifo_async_conversion():
    inst = bench_conversion_fifo_async()
    inst.convert(hdl='Verilog', directory=None)


def test_fifo_async_verify():
    verify.simulator = 'iverilog'
    inst = bench_conversion_fifo_async()
    assert inst.verify_convert() == 0


if __name__ == '__main__':
    test_async_fifo()
    test_fifo_async_conversion()
    test_fifo_async_verify()
