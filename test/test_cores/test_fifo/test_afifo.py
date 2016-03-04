#
# Copyright (c) 2014 Christopher L. Felton
#

from __future__ import division
from __future__ import print_function

from argparse import Namespace

from myhdl import *

from rhea.system import FIFOBus
from rhea.cores.fifo import fifo_async

from rhea.utils.test import run_testbench


def test_afifo(args=None):
    """ verify the asynchronous FIFO    
    """
    if args is None:
        args = Namespace(width=8, size=16, name='test')
    
    reset = ResetSignal(0, active=1, async=True)
    wclk, rclk = [Signal(bool(0)), Signal(bool(0))]
    fbus = FIFOBus(width=args.width, size=args.size)
    start = Signal(bool(0))

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # clocks
    @always(delay(10))
    def tbwclk():
        wclk.next = not wclk
    
    @always(delay(12))
    def tbrclk():
        rclk.next = not rclk

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # FIFO writer and reader
    _wr = Signal(bool(0))

    @instance
    def tb_always_wr():
        was_full = False
        wrd = modbv(0)[args.width:]
        while True:
            if start:
                break
            yield wclk.posedge

        while True:
            yield wclk.posedge
            if not fbus.full and was_full:
                was_full = False
                for _ in range(17):
                    yield wclk.posedge
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
        rdd = modbv(0)[args.width:]
        while True:
            if start:
                break
            yield wclk.posedge

        while True:
            try:
                yield rclk.posedge
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
                    yield rclk.posedge
                raise err

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def _test1():
        
        tbdut = fifo_async(reset, wclk, rclk, fbus)
                
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
                    
            # Test overflows        
            # Test underflows        
            # Test write / read same time
            
            raise StopSimulation
        
        return tbdut, tbwclk, tbrclk, tbstim

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def _test2():
        
        tbdut = fifo_async(reset, wclk, rclk, fbus)
         
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

        return (tbdut, tbwclk, tbrclk, tb_always_wr, tb_always_wr_gate, 
                tb_always_rd, tbstim)

    # run the tests
    for tt in (_test1, _test2,):
        run_testbench(tt)


if __name__ == '__main__':
    test_afifo()
