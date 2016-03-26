#
# Copyright (c) 2014 Christopher L. Felton
#

from __future__ import division
from __future__ import print_function

import os
from argparse import Namespace

from myhdl import *

from rhea.system import FIFOBus
from rhea.cores.fifo import fifo_sync
from rhea.utils.test import run_testbench


def test_sfifo(args=None):
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

    def _bench_sync_fifo():
        
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

    run_testbench(_bench_sync_fifo)


if __name__ == '__main__':
    for size in (16, 64, 256):
        args = Namespace(width=8, size=size, name='test')
        test_sfifo(args=args)
