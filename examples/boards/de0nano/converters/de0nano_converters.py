
from __future__ import division

"""
This example uses the A/D converter and the accelerometer.
The example retrieves the samples from the converters and ...
"""

from myhdl import (Signal, intbv, always_comb, always_seq,
                   always, TristateSignal, instances)

from rhea.system import (Clock, Reset, Global, FIFOBus)

from rhea.cores.converters import adc128s022
from rhea.cores.spi import spi_controller
from rhea.cores.spi import SPIBus
from rhea.system import FIFOBus
import rhea.build as build
from rhea.build.boards import get_board

# board defintion for the automated flow
brd = None


def de0nano_converters(clock, reset, led,
    adc_cs_n, adc_saddr, adc_sdat, adc_sclk,
    i2c_sclk, i2c_sdat, g_sensor_cs_n, g_sensor_int):
    """    
    The port names are the same as those in the board definition
    (names in the user manual) for automatic mapping by the 
    rhea.build automation.
    """
    glbl = Global(clock, reset)
    adcbus = SPIBus()
    #adc_saddr, adc_sdat, adc_cs_n, adc_sclk = (
    #    adcbus.mosi, adcbus.miso, adcbus.cns, adcbus.sck)
    adcbus.mosi, adcbus.miso, adcbus.csn, adcbus.sck = (
        adc_saddr, adc_sdat, adc_cs_n, adc_sclk)
    fifobus = FIFOBus(width=16, size=16)
    channel = Signal(intbv(0, min=0, max=8))

    # instantiate the ADC controller (retieves samples)
    gconv = adc128s022(glbl, fifobus, adcbus, channel)

    # read the samples out of the FIFO interface
    @always(clock.posedge)
    def rtl_read():
        fifobus.rd.next = not fifobus.empty

    # for now assign the samples to the  LEDs for viewing
    @always_seq(clock.posedge, reset=reset)
    def rtl_leds():
        led.next = fifobus.rdata[12:4]

    return instances()


# the default port map
# @todo: should be able to extact this from the board
# @todo: definition:
# @todo: portmap = brd.map_ports(de0nano_converters)    
de0nano_converters.portmap = {
    'clock': Clock(0, frequency=50e6),
    'reset': Reset(0, active=0, async=True),
    'leds': Signal(intbv(0)[8:]),
    'adc_cs_n': Signal(bool(1)),
    'adc_saddr': Signal(bool(1)),
    'adc_sdat': Signal(bool(1)),
    'adc_sclk': Signal(bool(1)),
    'i2c_sclk': Signal(bool(1)),
    'i2c_sdat': TristateSignal(bool(0)),
    'g_sensor_cs_n': Signal(bool(1)),
    'g_sensor_int': Signal(bool(1))
}


def build():
    global brd, flow
    brd = get_board('de0nano')
    flow = brd.get_flow(top=de0nano_converters)
    flow.run()

    
def program():
    global flow
    if flow is not None:
        flow.program()


if __name__ == '__main__':
    build()
    program()