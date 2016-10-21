#
# Copyright (c) 2014 Christopher L. Felton
# See the licence file in the top directory
#

from __future__ import division, print_function

import os
from argparse import Namespace

import pytest

import myhdl
from myhdl import (Signal, ResetSignal, intbv, always, always_comb,
                   instance, delay, StopSimulation,)
from myhdl.conversion import verify

from rhea.system import Signals, Global, Clock
from rhea.system import FIFOBus
from rhea.cores.fifo import fifo_sync
from rhea.utils.test import run_testbench, tb_default_args, tb_args


def test_fifo_sync(args=None):
    """ verify the synchronous FIFO
    """
    if args is None:
        args = Namespace(width=8, size=16, name='test')
    else:
        assert hasattr(args, 'width')
        assert hasattr(args, 'size')
    args = tb_default_args(args)

    reset = ResetSignal(0, active=1, async=True)
    clock = Clock(0, frequency=50e6)
    glbl = Global(clock, reset)
    fbus = FIFOBus(width=args.width)

    @myhdl.block
    def bench_fifo_sync():
        
        tbdut = fifo_sync(glbl, fbus, size=args.size)
        tbclk = clock.gen()
        
        @instance
        def tbstim():
            fbus.write_data.next = 0xFE
            reset.next = reset.active
            yield delay(33)
            reset.next = not reset.active
            for ii in range(5):
                yield clock.posedge

            # test the normal cases
            for num_bytes in range(1, args.size+1):

                # write some bytes
                for ii in range(num_bytes):
                    yield clock.posedge
                    fbus.write_data.next = ii + 0xCE
                    fbus.write.next = True

                yield clock.posedge
                fbus.write.next = False
                fbus.write_data.next = 0xFE

                # if 16 bytes written make sure FIFO is full
                yield clock.posedge
                if num_bytes == args.size:
                    assert fbus.full, "FIFO should be full!"
                    assert not fbus.empty, "FIFO should not be empty"
                
                # fbus.read.next = True
                # yield clock.posedge
                for ii in range(5):
                    yield clock.posedge
                    if not fbus.empty:
                        break

                for ii in range(num_bytes):
                    fbus.read.next = True
                    yield clock.posedge
                    assert fbus.read_valid
                    assert fbus.read_data == ii + 0xCE, \
                        "rdata %x ii %x " % (fbus.read_data, ii + 0xCE)

                fbus.read.next = False
                yield clock.posedge
                assert fbus.empty

            raise StopSimulation

        w = args.width
        write_data, read_data = Signals(intbv(0)[w:], 2)

        @always_comb
        def tbmon():
            write_data.next = fbus.write_data
            read_data.next = fbus.read_data

        return tbdut, tbclk, tbstim, tbmon

    run_testbench(bench_fifo_sync, args=args)


def test_fifo_sync_random():
    """Test random reads and writes at random times
    """
    pass


@myhdl.block
def bench_convserion_fifo_sync():
    args = Namespace(width=8, size=16, name='test')
    reset = ResetSignal(0, active=1, async=True)
    clock = Signal(bool(0))
    glbl = Global(clock, reset)
    fbus = FIFOBus(width=args.width)

    tbdut = fifo_sync(glbl, fbus, size=args.size)

    @instance
    def tbclk():
        clock.next = False
        while True:
            yield delay(5)
            clock.next = not clock

    @instance
    def tbstim():
        print("start simulation")
        fbus.read.next = False
        fbus.write.next = False
        fbus.clear.next = False
        fbus.write_data.next = 0
        reset.next = True
        yield delay(20)
        reset.next = False
        yield clock.posedge

        print("r, w, e, f")
        print("%d, %d, %d, %d, should be empty" % (
            fbus.read, fbus.write, fbus.empty, fbus.full,))
        assert fbus.empty

        fbus.write.next = True
        fbus.write_data.next = 0xAA
        yield clock.posedge
        fbus.write.next = False
        yield clock.posedge
        print("%d, %d, %d, %d, should not be empty" % (
            fbus.read, fbus.write, fbus.empty, fbus.full,))
        assert not fbus.empty
        print("FIFO count %d  (%d%d%d%d)" % (
            fbus.count, fbus.read, fbus.write, fbus.empty, fbus.full))

        print("more writes")
        fbus.write.next = True
        fbus.write_data.next = 1
        for ii in range(15):
            yield clock.posedge
            print("FIFO count %d  (%d%d%d%d)" % (
                fbus.count, fbus.read, fbus.write, fbus.empty, fbus.full))
            fbus.write_data.next = ii + 2
        fbus.write.next = False
        yield clock.posedge
        print("FIFO count %d  (%d%d%d%d)" % (
            fbus.count, fbus.read, fbus.write, fbus.empty, fbus.full))
        yield clock.posedge
        print("%d, %d, %d, %d, should be full" % (
            fbus.read, fbus.write, fbus.empty, fbus.full,))
        # assert fbus.full

        fbus.read.next = True
        assert fbus.read_data == 0xAA
        yield fbus.read_valid.posedge
        fbus.read.next = False
        yield delay(1)
        print("%d, %d, %d, %d" % (
            fbus.read, fbus.write, fbus.empty, fbus.full,))
        yield clock.posedge
        yield clock.posedge

        fbus.read.next = True
        for ii in range(15):
            print("FIFO count %d  data %d (%d%d%d%d)" % (
                fbus.count, fbus.read_data, fbus.read, fbus.write,
                fbus.empty, fbus.full))
            yield clock.posedge

        fbus.read.next = False
        yield clock.posedge
        print("%d, %d, %d, %d" % (
            fbus.read, fbus.write, fbus.empty, fbus.full,))

        print("end simulation")
        raise StopSimulation

    @instance
    def tbmon():
        clockticks = 0
        init_mem = False
        read_data = 0
        while True:
            if not reset:
                if not init_mem:
                    read_data = 0
                else:
                    read_data = int(fbus.read_data)

                print("%d: %d %d %d %d .. (w) %d %d .. (r) %d %d %d" % (
                    clockticks,
                    fbus.clear, fbus.empty, fbus.full, fbus.count,
                    fbus.write, fbus.write_data,
                    fbus.read, fbus.read_valid, read_data,
                ))

            clockticks = clockticks + 1
            if not fbus.empty:
                init_mem = True
            yield clock.posedge

    return tbdut, tbclk, tbstim, tbmon


def test_fifo_sync_conversion():
    # need this to set the output directory can't be
    # included in the test_fifo_sync_verify
    inst = bench_convserion_fifo_sync()
    inst.convert(hdl='Verilog', directory=None)


@pytest.mark.xfail()
def test_fifo_sync_verify():
    verify.simulator = 'iverilog'
    inst = bench_convserion_fifo_sync()
    assert inst.verify_convert() == 0


if __name__ == '__main__':
    args = tb_args()
    args.width, args.size = 8, 8
    test_fifo_sync(args=args)