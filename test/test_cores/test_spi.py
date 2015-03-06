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


from pprint import pprint

from myhdl import *

from mn.cores.spi import m_spi
from mn.cores.spi import SPIBus

from mn.models.spi import SPIEEPROM

from mn.system import Clock,Reset
from mn.system import Wishbone
from mn.system import FIFOBus 

from mn.utils.test import *

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
    reset = Reset(0, active=1, async=False)
    regbus = Wishbone(clock, reset)    
    fiforx,fifotx = FIFOBus(size=16), FIFOBus(size=16)
    spiee = SPIEEPROM()
    spibus = SPIBus()
    asserr = Signal(bool(0))
    
    def _test_spi():
        tbdut = m_spi(clock, reset, regbus, fiforx, fifotx, spibus)
        rf = regbus.regfiles[0]
        tbeep = spiee.gen(clock, reset, spibus)
        tbclk = clock.gen(hticks=5)

        pprint(vars(rf))
        @instance
        def tbstim():
            yield reset.pulse(33)
            yield regbus.read(0x68)
            print(regbus.readval)

            raise StopSimulation
        
        return tbstim, tbdut, tbeep, tbclk

    tb_clean_vcd('_test_spi')
    Simulation(traceSignals(_test_spi)).run()
    
        
if __name__ == '__main__':
    test_spi()
    #convert()
