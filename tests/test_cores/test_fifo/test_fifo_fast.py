#
# Copyright (c) 2014 Christopher L. Felton
# See the licence file in the top directory
#

from __future__ import division, print_function

import random
from random import randrange
from argparse import Namespace

import pytest
import myhdl
from myhdl import (Signal, ResetSignal, always, delay, instance,
                   StopSimulation)

from rhea.system import FIFOBus, Global, Clock, Reset
import rhea.cores as cores
from rhea.cores.fifo import fifo_fast

from rhea.utils.test import run_testbench


random.seed(3)


def test_fifo_fast(args=None):
    """ verify the synchronous FIFO
    """
    clock = Clock(0, frequency=50e6)
    reset = Reset(0, active=0, async=True)

    if args is None:
        args = Namespace(width=8, size=16, name='test')
    else:
        # @todo: verify args has the attributes needed for the FIFOBus
        pass 

    fbus = FIFOBus(width=args.width)
    glbl = Global(clock, reset)

    @myhdl.block
    def bench_fifo_fast():
        
        # @todo: use args.fast, args.use_srl_prim
        tbdut = cores.fifo.fifo_fast(
            glbl, fbus, size=args.size, use_srl_prim=False
        )
        
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

                    # print('nbyte %x wdata %x' % (num_bytes, ii))

                    fbus.write_data.next = ii
                    fbus.write.next = True
                    # wait for 1 clock cyle to 
                    # allow the fifo ops to occur
                    yield clock.posedge

                fbus.write.next = False
                fbus.write_data.next = 0xFE

                # if 16 bytes written make sure FIFO is full
                yield clock.posedge
                if num_bytes == args.size:
                    assert fbus.count == args.size
                    assert fbus.full, "FIFO should be full!"
                    assert not fbus.empty, "FIFO should not be empty"
                
                for cc in range(5):
                    yield clock.posedge

                for ii in range(num_bytes ):
                    fbus.read.next = True
                    yield clock.posedge
                    # print("rdata %x ii %x " % (fbus.read_data, ii))
                    assert fbus.read_valid
                    assert fbus.read_data == ii, "rdata %x ii %x " % (fbus.read_data, ii)

                fbus.read.next = False
                yield clock.posedge
                assert fbus.empty

            fbus.clear.next = True
            yield clock.posedge
            fbus.clear.next = not fbus.clear
            for ii in range(5):
                yield clock.posedge

            raise StopSimulation

        return myhdl.instances()

    # normal fifo r/w
    run_testbench(bench_fifo_fast)


def test_overflow_ffifo(args=None):
    """ verify the synchronous FIFO
    """
    reset = ResetSignal(0, active=1, async=True)
    clock = Signal(bool(0))

    if args is None:
        args = Namespace(width=8, size=16, name='test')
    else:
        # @todo: verify args has the attributes needed for the FIFOBus
        pass 

    fbus = FIFOBus(width=args.width)
    glbl = Global(clock, reset)

    @myhdl.block
    def bench_fifo_overflow():
        # @todo: use args.fast, args.use_srl_prim
        tbdut = cores.fifo.fifo_fast(glbl, fbus,
                                     size=args.size, use_srl_prim=False)

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

            # write more bytes       
            rand = randrange(args.size+2,2*args.size+1)
            for num_bytes in range(args.size, rand):
                            
                for ii in range(num_bytes):
                    try:
                        fbus.write_data.next = ii
                        fbus.write.next = True
                        yield clock.posedge
                    except ValueError:
                        assert fbus.count == args.size
                        assert fbus.full, "FIFO should be full!" 
                        assert not fbus.empty, "FIFO should not be empty" 
                    else:
                        assert fbus.count <= args.size
                        if fbus.count < args.size:
                            assert not fbus.full
                        
                fbus.write.next = False
                fbus.write_data.next = 0xFE
                for cc in range(5):                
                    yield clock.posedge

                for ii in range(args.size):
                    fbus.read.next = True
                    yield clock.posedge
                    assert fbus.read_valid
                    assert fbus.read_data == ii, "rdata %x ii %x " % (fbus.read_data, ii)

                fbus.read.next = False
                yield clock.posedge
                assert fbus.empty

            fbus.clear.next = True
            yield clock.posedge
            fbus.clear.next = not fbus.clear
            for ii in range(5):
                yield clock.posedge
            raise StopSimulation

        return myhdl.instances()

    for kk in range(100):
        with pytest.raises(ValueError):
            run_testbench(bench_fifo_overflow)


# test underflow
# should give a ValueError
# but instead gives an assertion error
@pytest.mark.xfail
def test_underflow_fifo_fast(args=None):
    """ verify the synchronous FIFO
    """
    reset = ResetSignal(0, active=1, async=True)
    clock = Signal(bool(0))

    if args is None:
        args = Namespace(width=8, size=16, name='test')
    else:
        # @todo: verify args has the attributes needed for the FIFOBus
        pass 

    fbus = FIFOBus(width=args.width)
    glbl = Global(clock, reset)

    @myhdl.block
    def bench_fifo_underflow():
        # @todo: use args.fast, args.use_srl_prim
        tbdut = cores.fifo.fifo_fast(
            glbl, fbus, size=args.size, use_srl_prim=False
        )
    
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
   
            rand = randrange(args.size+2, 2*args.size+1)
            for num_bytes in range(args.size, rand):
                            
                for ii in range(args.size):
                    try:
                        fbus.write_data.next = ii
                        fbus.write.next = True
                        yield clock.posedge
                    except ValueError:
                        assert fbus.count == args.size
                        assert fbus.full, "FIFO should be full!" 
                        assert not fbus.empty, "FIFO should not be empty" 
                    else:
                        assert fbus.count <= args.size
                        if (fbus.count < args.size):
                            assert not fbus.full
                        
                fbus.write.next = False
                fbus.write_data.next = 0xFE
                for delay_clk in range(5):
                    yield clock.posedge

                if ii == (args.size - 1):
                    assert fbus.count == args.size
                    assert fbus.full, "FIFO should be full!"
                    assert not fbus.empty, "FIFO should not be empty"

                yield clock.posedge

                for ii in range(num_bytes):
                    try:
                        fbus.read.next = True
                        yield clock.posedge
                        # yield clock.posedge
                        # test works for 2 
                        # yield clock.posedge stmts
                    except ValueError:
                        assert fbus.empty
                    else:   
                        # print("rdata %x ii %x " % (fbus.read_data, ii))
                        assert fbus.read_valid
                        assert fbus.read_data == ii, "rdata %x ii %x " % (fbus.read_data, ii)
                        
                fbus.read.next = False
                yield clock.posedge
                assert fbus.empty

            fbus.clear.next = True
            yield clock.posedge
            fbus.clear.next = not fbus.clear
            for ii in range(5):
                yield clock.posedge
            raise StopSimulation

        return myhdl.instances()

    with pytest.raises(ValueError):
        run_testbench(bench_fifo_underflow)


def test_rw_ffifo(args=None):
    """ verify the synchronous FIFO
    Read and write at the same time, the FIFO should remain
    unchanged.
    """
    clock = Clock(0, frequency=50e6)
    reset = Reset(0, active=0, async=True)

    if args is None:
        args = Namespace(width=8, size=16, name='test')
    else:
        # @todo: verify args has the attributes needed for the FIFOBus
        pass

    fbus = FIFOBus(width=args.width)
    glbl = Global(clock, reset)

    @myhdl.block
    def bench_rw_fifo_fast():
        
        # @todo: use args.fast, args.use_srl_prim
        tbdut = cores.fifo.fifo_fast(
            glbl, fbus, size=args.size, use_srl_prim=False
        )

        @instance
        def tbstim():
            fbus.write_data.next = 0xFE
            reset.next = reset.active
            yield delay(33)
            reset.next = not reset.active
            for ii in range(5):
                yield clock.posedge

            for num_bytes in range(1, args.size):

                # write some bytes
                for ii in range(num_bytes):
                    # print('nbyte %x wdata %x' % (num_bytes, ii))
                   
                    fbus.write_data.next = ii
                    fbus.write.next = True
                    yield clock.posedge

                fbus.write.next = False
                fbus.write_data.next = 0xFE
                a = fbus.count
                               
                for cc in range(5):
                    yield clock.posedge

                # if 16 bytes written make sure FIFO is full
                yield clock.posedge
                if num_bytes == args.size:
                    assert fbus.count == args.size
                    assert fbus.full, "FIFO should be full!"
                    assert not fbus.empty, "FIFO should not be empty"
                
                # r/w at the same time, should not
                # change the size of the fifo
                for ii in range(num_bytes, args.size):
                    fbus.write_data.next = ii
                    fbus.write.next = True
                    fbus.read.next = True
                    yield clock.posedge
                    assert fbus.read_data == (ii - num_bytes)
                    assert fbus.read_valid
                    if ii == 0:
                        assert fbus.empty
                    else:
                        assert not fbus.empty

                fbus.write.next = False
                fbus.write_data.next = 0xFE
                fbus.read.next = False
                        
                assert a == fbus.count
                for cc in range(5):
                    yield clock.posedge
                
                # read remaining bytes
                for ii in range(num_bytes):
                    fbus.read.next = True
                    yield clock.posedge
                    # print("rdata %x ii %x " % (fbus.read_data, ii))
                    assert fbus.read_valid
                    assert fbus.read_data == ((args.size - num_bytes) + ii), \
                                             "rdata %x ii %x " % (fbus.read_data, \
                                             ((args.size - num_bytes) + ii))

                fbus.read.next = False
                yield clock.posedge
                assert fbus.empty

            fbus.clear.next = True
            yield clock.posedge
            fbus.clear.next = not fbus.clear
            for ii in range(5):
                yield clock.posedge

            raise StopSimulation

        return myhdl.instances()
           
    # r/w at the same time
    for trial in range(100):   
         run_testbench(bench_rw_fifo_fast)


if __name__ == '__main__':
    for size in (4, 8, 16):
        args = Namespace(width=8, size=size, name='test')
        test_fifo_fast(args=args)
