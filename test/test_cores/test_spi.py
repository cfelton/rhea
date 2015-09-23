#
# Copyright (c) 2013-2015 Christopher L. Felton
#

import traceback
import pytest

from myhdl import *

from rhea.cores.spi import spi_controller
from rhea.cores.spi import SPIBus

from rhea.models.spi import SPIEEPROM

from rhea.system import Global, Clock, Reset
from rhea.system import Wishbone
from rhea.system import FIFOBus

from rhea.utils.test import run_testbench


def m_test_top(clock, reset, sck, mosi, miso, ss):
    # @todo: create a top-level for conversion ...
    g_spi = spi_controller()
    return g_spi


def convert():
    clock = Clock(0, frequency=50e6)
    reset = Reset(0, active=1, async=False)
    sck = Signal(bool(0))
    mosi = Signal(bool(0))
    miso = Signal(bool(0))
    ss = Signal(bool(0))

    toVerilog.directory = 'output/'
    toVerilog(m_test_top, clock, reset, sck, mosi, miso, ss)
    toVHDL.directory = 'output/'
    toVHDL(m_test_top, clock, reset, sck, mosi, miso, ss)


def test_spi():
    
    base_address = ba = 0x400
    clock = Clock(0, frequency=50e6)
    reset = Reset(0, active=1, async=False)
    glbl = Global(clock, reset)
    regbus = Wishbone(glbl)    
    fiforx, fifotx = FIFOBus(size=16), FIFOBus(size=16)
    spiee = SPIEEPROM()
    spibus = SPIBus()
    asserr = Signal(bool(0))
    
    def _bench_spi():
        tbdut = spi_controller(glbl, regbus, 
                          fiforx, fifotx, spibus,
                          base_address=base_address)
        tbeep = spiee.gen(clock, reset, spibus)
        tbclk = clock.gen(hticks=5)
        # grab all the register file outputs
        tbmap = regbus.m_per_outputs()

        # get a reference to the SPI register file
        rf = regbus.regfiles['SPI_000']
        # dumpy the registers for the SPI peripheral
        print("SPI register file")
        for name, reg in rf.registers.items():
            print("  {0} {1:04X} {2:04X}".format(name, reg.addr, int(reg)))
        print("")

        @instance
        def tbstim():            
            yield reset.pulse(33)
            yield delay(100)
            yield clock.posedge
            
            try:
                # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                # loop through the registers and check the default 
                # values, these are the offset values.
                for addr, sig in rf.roregs:
                    yield regbus.read(addr+ba)
                    assert regbus.get_read_data() == int(sig), \
                        "Invalid read-only value"

                for addr, sig in rf.rwregs:
                    # need to skip the FIFO read / write
                    if addr in (rf.sptx.addr, rf.sprx.addr,):
                        pass
                    else:
                        yield regbus.read(addr+ba)
                        assert regbus.get_read_data() == int(sig), \
                            "Invalid default value"

                # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                # enable the system         
                print("enable the SPI core")
                yield regbus.write(rf.spst.addr, 0x02)  # register data drives fifo
                yield regbus.write(rf.spcr.addr, 0x9A)  # default plus enable (98 + 02)

                print("write to the transmit register")
                for data in (0x02, 0x00, 0x00, 0x00, 0x55):
                    print("\nwriting to sptx {:02x}".format(data))
                    yield regbus.write(rf.sptx.addr, data)

                print("")
                yield regbus.read(rf.sptc.addr)
                print("TX FIFO count {}".format(regbus.get_read_data()))

                yield regbus.read(rf.sprc.addr)
                print("RX FIFO count {}".format(regbus.get_read_data()))

                yield delay(1000)

                print("wait for return bytes")
                for ii in range(1000):
                    yield regbus.read(rf.sprc.addr)
                    if regbus.get_read_data() == 5:
                        break
                    yield delay(10)
                
                # verify bytes received and not timeout
                print("RX FIFO count {}".format(regbus.get_read_data()))
                assert regbus.get_read_data() == 5
                
                print("read the returned bytes")
                for ii in range(5):
                    yield regbus.read(rf.sprx.addr)
                    print("spi readback {0}".format(regbus.get_read_data()))

            except Exception as err:
                print("@W: exception {0}".format(err))                
                yield delay(100)
                traceback.print_exc()
                raise err

            yield delay(100)
            raise StopSimulation
        
        return tbstim, tbdut, tbeep, tbclk, tbmap

    run_testbench(_bench_spi)


@pytest.mark.xfail
def test_convert():
    convert()


if __name__ == '__main__':
    test_spi()
