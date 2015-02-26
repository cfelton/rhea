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
from mn.cores.fifo import m_fifo_async

def test_afifo(args=None):
    """ verify the asynchronous FIFO    
    """
    if args is None:
        args = Namespace(width=8, size=16, name='test')
    
    reset   = ResetSignal(0, active=1, async=True)
    wclk,rclk = [Signal(bool(0)), Signal(bool(0))]
    fbus    = FIFOBus(args=args)
    start = Signal(bool(0))

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # clocks
    @always(delay(10))
    def tbwclk():
        wclk.next = not wclk
    
    @always(delay(12))
    def tbrclk():
        rclk.next = not rclk

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
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
                fbus.wdata.next = wrd
                _wr.next = True
                yield delay(1)
                if not fbus.full:
                    wrd[:] += 1
            else:
                _wr.next = False
                was_full = True

    @always_comb
    def tb_always_wr_gate():
        fbus.wr.next = _wr and not fbus.full

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
                    fbus.rd.next = True
                else:
                    fbus.rd.next = False
                    
                if fbus.rvld:
                    tmp = fbus.rdata
                    assert tmp == rdd, " %d != %d " % (tmp, rdd)
                    rdd[:] += 1
            except AssertionError, err:
                for _ in range(10):
                    yield rclk.posedge
                raise err

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def _test1():
        
        tbdut = m_fifo_async(reset, wclk, rclk, fbus)
                
        @instance
        def tbstim():
            print("start test 1")
            fbus.wdata.next = 0xFE
            reset.next = reset.active
            yield delay(3*33)
            reset.next = not reset.active

            # reset is delayd by at least two
            for ii in range(5):
                yield wclk.posedge
        
            # test normal cases
            for num_bytes in range(1, args.size+1):
        
                # Write some byte
                for ii in range(num_bytes):
                    #print('%d wr %d' % (num_bytes, ii))
                    yield wclk.posedge
                    fbus.wdata.next = ii
                    fbus.wr.next  = True
                    
                yield wclk.posedge
                fbus.wr.next = False
        
                # If 16 bytes written make sure FIFO is full
                yield wclk.posedge
                if num_bytes == args.size:
                    assert fbus.full, "FIFO should be full!"
        
                while fbus.empty:
                    yield rclk.posedge
                    
                fbus.rd.next = True
                yield rclk.posedge
                for ii in range(num_bytes):
                    yield rclk.posedge
                    fbus.rd.next = True
                    #print("rdata %x ii %x " % (fbus.rdata, ii))
                    assert fbus.rvld
                    assert fbus.rdata == ii, "rdata %x ii %x " % (fbus.rdata, ii)
        
                yield rclk.posedge
                fbus.rd.next = False
                yield rclk.posedge
                assert fbus.empty
                    
            # Test overflows        
            # Test underflows        
            # Test write / read same time
            
            raise StopSimulation
        
        return tbdut, tbwclk, tbrclk, tbstim

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def _test2():
        
        tbdut = m_fifo_async(reset, wclk, rclk, fbus)
         
        @instance
        def tbstim():
            print("start test 2")
            fbus.wdata.next = 0xFE
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

    for tt in (_test1, _test2,): 
        traceSignals.name = 'vcd/test_afifo_%s' % (tt.func_name)
        if os.path.isfile(traceSignals.name+'.vcd'):
            os.remove(traceSignals.name+'.vcd')
        g = traceSignals(tt)
        Simulation(g).run()

    #traceSignals.name = 'vcd/test_afifo'
    #if os.path.isfile(traceSignals.name+'.vcd'):
    #    os.remove(traceSignals.name+'.vcd')
    #g = traceSignals(_test1)
    #Simulation(g).run()

if __name__ == '__main__':
    test_afifo()
