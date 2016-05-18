#
# Copyright (c) 2014 Christopher L. Felton
#

from __future__ import division, print_function

import os
from argparse import Namespace

import myhdl
from myhdl import (Signal, ResetSignal, always, instance, delay, 
                   StopSimulation,)
from myhdl.conversion import verify

from rhea.system import FIFOBus
from rhea.cores.fifo import fifo_sync
from rhea.utils.test import run_testbench


def test_fifo_sync(args=None):
    """ verify the synchronous FIFO
    """

    if args is None:
        args = Namespace(width=8, size=16, name='test')
    else:
        # @todo: verify args has the attributes needed for the FIFOBus
        pass 

    reset = ResetSignal(0, active=1, async=True)
    clock = Signal(bool(0))
    fbus = FIFOBus(width=args.width, size=args.size)

    def bench_fifo_sync():
        
        # @todo: use args.fast, args.use_srl_prim
        tbdut = fifo_sync(clock, reset, fbus)

        @always(delay(10))
        def tbclk():
            clock.next = not clock
        
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
                    fbus.write_data.next = ii
                    fbus.write.next = True

                yield clock.posedge
                fbus.write.next = False
                fbus.write_data.next = 0xFE

                # if 16 bytes written make sure FIFO is full
                yield clock.posedge
                if num_bytes == args.size:
                    assert fbus.full, "FIFO should be full!"
                    assert not fbus.empty, "FIFO should not be empty"
                
                fbus.read.next = True
                yield clock.posedge
                for ii in range(num_bytes):
                    yield clock.posedge
                    fbus.read.next = True
                    assert fbus.read_valid
                    assert fbus.read_data == ii, "rdata %x ii %x " % (fbus.read_data, ii)

                fbus.read.next = False
                yield clock.posedge
                assert fbus.empty

            # Test overflows        
            # Test underflows        
            # Test write / read same time

            raise StopSimulation

        return tbdut, tbclk, tbstim

    run_testbench(bench_fifo_sync)


def test_fifo_sync_conversion():
    # @todo: if the myhdl version is 1.0 or greater 
    #        use "iverilog"
    verify.simulator = "iverilog"
    args = Namespace(width=8, size=16, name='test')

    def bench():
        reset = ResetSignal(0, active=1, async=True)
        clock = Signal(bool(0))
        fbus = FIFOBus(width=args.width, size=args.size)
        
        tbdut = fifo_sync(clock, reset, fbus)

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
            reset.next = True
            yield delay(20)
            reset.next = False
            yield clock.posedge
            
            print("r, w, e, f")
            print("%d, %d, %d, %d, should be empty"  % (
                fbus.read, fbus.write, fbus.empty, fbus.full,))
            assert fbus.empty

            fbus.write.next = True
            fbus.write_data.next = 0xAA
            yield clock.posedge
            fbus.write.next = False
            yield clock.posedge
            print("%d, %d, %d, %d, should not be empty"  % (
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
            print("%d, %d, %d, %d, should be full"  % (
                fbus.read, fbus.write, fbus.empty, fbus.full,))
            # assert fbus.full

            fbus.read.next = True
            assert fbus.read_data == 0xAA
            yield fbus.read_valid.posedge
            fbus.read.next = False
            yield delay(1)
            print("%d, %d, %d, %d"  % (
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
            print("%d, %d, %d, %d"  % (
                fbus.read, fbus.write, fbus.empty, fbus.full,))

            print("end simulation")
            raise StopSimulation

        return tbdut, tbclk, tbstim

    myhdl.toVerilog.directory = None
    assert verify(bench) == 0


if __name__ == '__main__':
    for size in (16, 64, 256):
        args = Namespace(width=8, size=size, name='test')
        test_fifo_sync(args=args)
