#
# Copyright (c) 2014 Christopher L. Felton
#
# Permission is hereby granted, free of charge, to any person obtaining a 
# copy of this software and associated documentation files (the "Software"), 
# to deal in the Software without restriction, including without limitation 
# the rights to use, copy, modify, merge, publish, distribute, sublicense, 
# and/or sell copies of the Software, and to permit persons to whom the 
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included 
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS 
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL 
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN 
# THE SOFTWARE.
#

from __future__ import division
from __future__ import print_function

import os
from argparse import Namespace

from myhdl import *

from mn.system import FIFOBus
from mn.cores.fifo import m_fifo_sync

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
    fbus = FIFOBus(args=args)

    def _test():
        
        # @todo: use args.fast, args.use_srl_prim
        tbdut = m_fifo_sync(clock, reset, fbus)

        @always(delay(10))
        def tbclk():
            clock.next = not clock
        
        @instance
        def tbstim():
            fbus.wdata.next = 0xFE
            reset.next = reset.active
            yield delay(33)
            reset.next = not reset.active
            for ii in range(5):
                yield clock.posedge

            # test the normal cases
            for num_bytes in range(1, args.size+1):

                # write some bytes
                for ii in range(num_bytes):
                    #print('nbyte %x wdata %x' % (num_bytes, ii))
                    yield clock.posedge
                    fbus.wdata.next = ii
                    fbus.wr.next = True

                yield clock.posedge
                fbus.wr.next = False
                fbus.wdata.next = 0xFE

                # if 16 bytes written make sure FIFO is full
                yield clock.posedge
                if num_bytes == args.size:
                    assert fbus.full, "FIFO should be full!"
                    assert not fbus.empty, "FIFO should not be empty"
                
                fbus.rd.next = True
                yield clock.posedge
                for ii in range(num_bytes):
                    yield clock.posedge
                    fbus.rd.next = True
                    #print("rdata %x ii %x " % (fbus.rdata, ii))
                    assert fbus.rvld
                    assert fbus.rdata == ii, "rdata %x ii %x " % (fbus.rdata, ii)

                fbus.rd.next = False
                yield clock.posedge
                assert fbus.empty

            # Test overflows        
            # Test underflows        
            # Test write / read same time

            raise StopSimulation

        
        return tbdut, tbclk, tbstim

    traceSignals.name = 'vcd/test_fifo_sync_%d' % (args.size)
    if os.path.isfile(traceSignals.name+'.vcd'):
        os.remove(traceSignals.name+'.vcd')        
    g = traceSignals(_test)
    Simulation(g).run()

if __name__ == '__main__':
    for size in (16, 64, 256):
        args = Namespace(width=8, size=size, name='test')
        test_sfifo(args=args)
