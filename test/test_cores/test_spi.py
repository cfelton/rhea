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

from mn.cores.spi import m_spi
from mn.cores.spi import SPIBus

from mn.models.spi import SPIEEPROM

from mn.system import Clock,Reset
from mn.system import Wishbone
from mn.system import FIFOBus
from mn.system import RWData

# @todo: move utils to mn.utils, most of these functions
#        will be used by the *examples*.  Or move these
#        to myhdl_tools
#from _test_utils import *

def m_test_top(clock,reset,sck,mosi,miso,ss):
    # @todo:
    g_spi = m_spi()
    
def convert(to='ver'):
    clock = Clock(0, frequency=50e6)
    reset = Reset(0, active=1, async=False)
    sck = Signal(bool(0))
    mosi = Signal(bool(0))
    miso = Signal(bool(0))
    ss = Signal(bool(0))
       
    toVerilog(m_test_top, clock, reset, sck, mosi, miso, ss)
    toVHDL(m_test_top, clock, reset, sck, mosi, miso, ss)

def test_spi():
    
    clock = Clock(0, frequency=50e6)
    reset = Reset(0,active=1,async=False)
    regbus = Wishbone(clock,reset)    
    fiforx,fifotx = FIFOBus(),FIFOBus()
    spiee = SPIEEPROM()
    spibus = SPIBus()
    rwd = RWData()
    asserr = Signal(bool(0))
    
    def _test_spi():
        tb_dut = m_spi(clock,reset,regbus,fiforx,fifotx,spibus)
        tb_ee = spiee.gen(clock,reset,spibus)
        tb_clk = clock.gen(hticks=5)

        @instance
        def tb_stim():
            yield reset.pulse(33)
            yield regbus.read(0x400, rwd)
            print(rwd)

            raise StopSimulation
        
        return tb_stim, tb_dut, tb_ee, tb_clk

    Simulation(traceSignals(_test_spi)).run()
    
        
if __name__ == '__main__':
    test_spi()
    #convert()
