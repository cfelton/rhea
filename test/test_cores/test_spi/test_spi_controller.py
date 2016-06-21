#
# Copyright (c) 2013-2015 Christopher L. Felton
# See the licence file in the top directory
#

import traceback
import pytest
import argparse

import myhdl
from myhdl import (Signal, intbv, instance, always_comb,
                   delay, StopSimulation)

from rhea.cores.spi import spi_controller
from rhea.cores.spi import SPIBus

from rhea.models.spi import SPIEEPROM

from rhea.system import Global, Clock, Reset, Signals
from rhea.system import Wishbone
from rhea.system import FIFOBus

from rhea.utils.test import run_testbench, tb_convert, tb_args, tb_default_args


# global signals used by many
clock = Clock(0, frequency=100e6)
reset = Reset(0, active=1, async=True)
glbl = Global(clock, reset)
portmap = dict(
    glbl=glbl,
    spibus=SPIBus(),
    fifobus=FIFOBus(),
    cso=spi_controller.cso()
)


@myhdl.block
def spi_controller_top(clock, reset, sck, mosi, miso, ss):
    """SPI top-level for conversion testing"""
    glbl = Global(clock, reset)
    spibus = SPIBus(sck, mosi, miso, ss)
    fifobus = FIFOBus()

    cso = spi_controller.cso()
    cso.isstatic = True
    cfg_inst = cso.instances()

    spi_controller.debug = False
    spi_inst = spi_controller(glbl, spibus, fifobus, cso=cso)

    @always_comb
    def fifo_loopback():
        fifobus.write_data.next = fifobus.read_data
        fifobus.write.next = fifobus.read_valid
        fifobus.read.next = not fifobus.empty

    return myhdl.instances()


def convert():
    """convert the faux-top-level"""
    clock = Clock(0, frequency=50e6)
    reset = Reset(0, active=1, async=False)
    sck, mosi, miso, ss = Signals(bool(0), 4)
    inst = spi_controller_top(clock, reset, sck, mosi, miso, ss)
    tb_convert(inst)


def test_spi_controller_cso(args=None):
    args = tb_default_args(args)

    clock = Clock(0, frequency=50e6)
    reset = Reset(0, active=1, async=False)
    glbl = Global(clock, reset)
    spibus = SPIBus()

    # a FIFOBus to push-pull data from the SPI controller
    fifobus = FIFOBus(width=8)
    # control-status object for the SPI controller
    cso = spi_controller.cso()

    spiee = SPIEEPROM()
    asserr = Signal(bool(0))

    @myhdl.block
    def bench_spi_cso():
        spi_controller.debug = True    # enable debug monitors
        tbdut = spi_controller(glbl, spibus, fifobus, cso=cso)
        tbeep = spiee.process(clock, reset, spibus)
        tbclk = clock.gen(hticks=5)

        @instance
        def tbstim():
            yield reset.pulse(33)
            yield delay(100)
            yield clock.posedge

            try:
                # enable the SPI core
                cso.enable.next = True
                cso.bypass_fifo.next = True
                cso.loopback.next = True

                # write to the transmit FIFO
                values = (0x02, 0x00, 0x00, 0x00, 0x55)
                for data in values:
                    cso.tx_byte.next = data
                    cso.tx_write.next = True
                    yield clock.posedge
                cso.tx_write.next = False

                while cso.tx_fifo_count > 0:
                    yield delay(100)

                while cso.rx_fifo_count < 5:
                    yield delay(100)

                ii, nticks = 0, 0
                while ii < len(values):
                    if cso.rx_empty:
                        cso.rx_read.next = False
                    else:
                        cso.rx_read.next = True
                    if cso.rx_byte_valid:
                        assert values[ii] == cso.rx_byte, \
                            "{:<4d}: data mismatch, {:02X} != {:02X}".format(
                                ii, int(values[ii]), int(cso.rx_byte))
                        ii += 1
                        nticks = 0
                    yield clock.posedge, cso.rx_empty.posedge
                    cso.rx_read.next = False

                    if nticks > 30:
                        raise TimeoutError
                    nticks += 1

                cso.rx_read.next = False
                yield clock.posedge

            except AssertionError as err:
                asserr.next = True
                print("@E: assertion {}".format(err))
                yield delay(100)
                traceback.print_exc()
                raise err

            raise StopSimulation

        # monitor signals for debugging
        tx_write, rx_read = Signals(bool(0), 2)

        @always_comb
        def tbmon():
            rx_read.next = cso.rx_read
            tx_write.next = cso.tx_write

        return tbdut, tbeep, tbclk, tbstim, tbmon

    run_testbench(bench_spi_cso, args=args)


# enable when the register-file automation is complete
@pytest.mark.xfail()
def test_spi_memory_mapped(args=None):
    args = tb_default_args(args)
    
    base_address = ba = 0x400
    clock = Clock(0, frequency=50e6)
    reset = Reset(0, active=1, async=False)
    glbl = Global(clock, reset)
    regbus = Wishbone(glbl)    
    fifobus = FIFOBus(size=16)
    spiee = SPIEEPROM()
    spibus = SPIBus()
    asserr = Signal(bool(0))

    @myhdl.block
    def bench_spi():
        tbdut = spi_controller(glbl, spibus, fifobus=fifobus, mmbus=regbus)
        tbeep = spiee.gen(clock, reset, spibus)
        tbclk = clock.gen(hticks=5)
        # grab all the register file outputs
        tbmap = regbus.interconnect()

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
                    yield regbus.readtrans(addr+ba)
                    assert regbus.get_read_data() == int(sig), \
                        "Invalid read-only value"

                for addr, sig in rf.rwregs:
                    # need to skip the FIFO read / write
                    if addr in (rf.sptx.addr, rf.sprx.addr,):
                        pass
                    else:
                        yield regbus.readtrans(addr+ba)
                        assert regbus.get_read_data() == int(sig), \
                            "Invalid default value"

                # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                # enable the system         
                print("enable the SPI core")
                yield regbus.writetrans(rf.spst.addr, 0x02)  # register data drives fifo
                yield regbus.writetrans(rf.spcr.addr, 0x9A)  # default plus enable (98 + 02)

                print("write to the transmit register")
                for data in (0x02, 0x00, 0x00, 0x00, 0x55):
                    print("\nwriting to sptx {:02x}".format(data))
                    yield regbus.writetrans(rf.sptx.addr, data)

                print("")
                yield regbus.readtrans(rf.sptc.addr)
                print("TX FIFO count {}".format(regbus.get_read_data()))

                yield regbus.readtrans(rf.sprc.addr)
                print("RX FIFO count {}".format(regbus.get_read_data()))

                yield delay(1000)

                print("wait for return bytes")
                for ii in range(1000):
                    yield regbus.readtrans(rf.sprc.addr)
                    if regbus.get_read_data() == 5:
                        break
                    yield delay(10)
                
                # verify bytes received and not timeout
                print("RX FIFO count {}".format(regbus.get_read_data()))
                assert regbus.get_read_data() == 5
                
                print("read the returned bytes")
                for ii in range(5):
                    yield regbus.readtrans(rf.sprx.addr)
                    print("spi readback {0}".format(regbus.get_read_data()))

            except Exception as err:
                print("@W: exception {0}".format(err))                
                yield delay(100)
                traceback.print_exc()
                raise err

            yield delay(100)
            raise StopSimulation
        
        return tbstim, tbdut, tbeep, tbclk, tbmap

    run_testbench(bench_spi, args=args)


def test_convert():
    convert()


if __name__ == '__main__':
    # test_spi_controller_cso(tb_args())
    test_convert()
