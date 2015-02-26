#
# Copyright (c) 2006-2013 Christopher L. Felton
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from myhdl import *

from mn.cores.fifo_ramp import m_fifo_ramp

from mn.system import Clock,Reset
from mn.system import Wishbone
from mn.system import FIFOBus
from mn.system import RWData

# @todo: move utils to mn.utils, most of these functions
#        will be used by the *examples*.  Or move these
#        to myhdl_tools
from _test_utils import *


def test_fifo_ramp():

    clock = Clock(0, frequency=50e6)
    reset = Reset(0,active=1,async=False)
    regbus = Wishbone(clock,reset)    
    fifobus = FIFOBus()

    def _test_fifo_ramp():
        tb_dut = m_fifo_ramp(clock,reset,regbus,fifobus,
                             base_address=0x0000)
        tb_rbor = regbus.m_per_outputs()
        tb_clk = clock.gen()
        
        rwd = RWData()
        asserr = Signal(bool(0))
                
        @instance 
        def tb_stim():
            try:
                yield delay(100)
                yield reset.pulse(111)

                # simply enable, enable the module and then
                # verify an incrementing pattern over the
                # fifobus
                rwd.wval = 1
                yield regbus.write(0x00, rwd)
                yield regbus.read(0x00, rwd)
                assert rwd.wval == rwd.rval, "cfg reg write failed"

                # monitor the bus until ?? ramps
                Nramps,rr = 128,0
                while rr < Nramps:
                    cnt = 0
                    for ii,sh in enumerate((24,16,8,0,)):
                        yield regbus.read(0x08+ii,rwd)
                        cnt = cnt | (rwd.rval << sh)
                    rr = cnt

            except AssertionError,err:
                asserr.next = True
                for _ in xrange(10):
                    yield clock.posedge
                raise err

            raise StopSimulation

        # monitor the values from the fifo bus, it should
        # be a simple "ramp" increasing values
        _mask = 0xFF
        _cval = Signal(modbv(0,min=0,max=256))
        @always(clock.posedge)
        def tb_mon():
            if fifobus.wr:
                assert _cval == fifobus.di
                _cval.next = _cval+1


        return tb_clk,tb_dut,tb_stim,tb_mon,tb_rbor

    tb_clean_vcd('_test_fifo_ramp')
    g = traceSignals(_test_fifo_ramp)
    Simulation(g).run()

if __name__ == '__main__':
    test_fifo_ramp()
                
