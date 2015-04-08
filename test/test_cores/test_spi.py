#
# Copyright (c) 2013-2015 Christopher L. Felton
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
from mn.system.regfile import Register

from mn.utils.test import *

def m_test_top(clock, reset, sck, mosi, miso, ss):
    # @todo: map top-level ports to interfaces
    #    for conversion.
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
    
    base_address = ba = 0x400
    clock = Clock(0, frequency=50e6)
    reset = Reset(0, active=1, async=False)
    regbus = Wishbone(clock, reset)    
    fiforx,fifotx = FIFOBus(size=16), FIFOBus(size=16)
    spiee = SPIEEPROM()
    spibus = SPIBus()
    asserr = Signal(bool(0))
    
    def _test_spi():
        tbdut = m_spi(clock, reset, regbus, 
                      fiforx, fifotx, spibus,
                      base_address=base_address)
        tbeep = spiee.gen(clock, reset, spibus)
        tbclk = clock.gen(hticks=5)
        # grab all the register file outputs
        tbmap = regbus.m_per_outputs()

        # get a reference to the SPI register file
        rf = regbus.regfiles['spi000']
        # dumpy the registers for the SPI peripheral
        for name,reg in rf.registers.iteritems():
            print("{0} {1:04X} {2:04X}".format(name, reg.addr, int(reg)))

        @instance
        def tbstim():            
            yield reset.pulse(33)

            try:
                #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                # loop through the registers and check the default 
                # values, these are the offset values.
                for addr,sig in rf.roregs:
                    yield regbus.read(addr+ba)
                    assert regbus.readval == int(sig)

                for addr,sig in rf.rwregs:
                    # need to skip the FIFO read / write
                    if addr in (0x68, 0x6C,):
                        pass
                    else:
                        yield regbus.read(addr+ba)
                        assert regbus.readval == int(sig)


                #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                # enable the system                
                yield regbus.write(rf.spcr.addr, 0x82)

                yield regbus.write(rf.sptx.addr, 0x02)
                yield regbus.write(rf.sptx.addr, 0x00)
                yield regbus.write(rf.sptx.addr, 0x00)
                yield regbus.write(rf.sptx.addr, 0x00)
                yield regbus.write(rf.sptx.addr, 0x55)

                yield regbus.read(rf.sptc.addr)
                print(regbus.readval)

                yield regbus.read(rf.sprc.addr)
                print(regbus.readval)

                yield delay(1000)

                for ii in range(1000):
                    yield regbus.read(rf.sprc.addr)
                    if regbus.readval == 5:
                        break
                    yield delay(1000)
                
                for ii in range(5):
                    yield regbus.read(rf.sprx.addr)
                    print("spi readback {0}".format(regbus.readval))
                

            except Exception, err:
                print("@W: exception {0}".format(err))                
                yield delay(100)
                raise err

            yield delay(100)
            raise StopSimulation
        
        return tbstim, tbdut, tbeep, tbclk, tbmap

    tb_clean_vcd('_test_spi')
    Simulation(traceSignals(_test_spi)).run()
    
        
if __name__ == '__main__':
    test_spi()
    #convert()
