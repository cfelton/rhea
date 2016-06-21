
"""
This example uses the A/D converter and the accelerometer.
The example retrieves the samples from the converters and ...
"""

from __future__ import division

import myhdl
from myhdl import (Signal, intbv, always_comb, always_seq,
                   always, TristateSignal, concat, instances)

from rhea.system import Clock, Reset, Global, FIFOBus
from rhea.cores.converters import adc128s022
from rhea.cores.spi import spi_controller
from rhea.cores.spi import SPIBus
from rhea.cores.video import VideoMemory
from rhea.cores.video import color_bars
from rhea.cores.video.lcd import lt24lcd
from rhea.cores.video.lcd import LT24Interface
from rhea.cores.misc import glbl_timer_ticks

import rhea.build as build
from rhea.build.boards import get_board

# board definition for the automated flow
brd, flow = None, None


@myhdl.block
def de0nano_converters(clock, reset, led,
    # ADC signals
    adc_cs_n, adc_saddr, adc_sdat, adc_sclk,
    # Accelerometer and I2C signals
    i2c_sclk, i2c_sdat, g_sensor_cs_n, g_sensor_int,
    # LT24 LCD display signals
    lcd_on, lcd_resetn, lcd_csn, lcd_rs,
    lcd_wrn, lcd_rdn, lcd_data
):
    """    
    The port names are the same as those in the board definition
    (names in the user manual) for automatic mapping by the 
    rhea.build automation.
    """
    # signals and interfaces
    glbl = Global(clock, reset)
    adcbus = SPIBus()
    adcbus.mosi, adcbus.miso, adcbus.csn, adcbus.sck = (
        adc_saddr, adc_sdat, adc_cs_n, adc_sclk)
    fifobus = FIFOBus(width=16)
    channel = Signal(intbv(0, min=0, max=8))

    # ----------------------------------------------------------------
    # global ticks
    t_inst = glbl_timer_ticks(glbl, include_seconds=True, user_timer=16)

    # ----------------------------------------------------------------
    # instantiate the ADC controller (retieves samples)
    conv_inst = adc128s022(glbl, fifobus, adcbus, channel)

    # read the samples out of the FIFO interface
    fiford = Signal(bool(0))

    @always(clock.posedge)
    def beh_read():
        fiford = not fifobus.empty

    @always_comb
    def beh_read_gate():
        fifobus.read.next = fiford and not fifobus.empty

    # for now assign the samples to the  LEDs for viewing
    heartbeat = Signal(bool(0))

    @always_seq(clock.posedge, reset=reset)
    def beh_leds():
        if glbl.tick_sec:
            heartbeat.next = not heartbeat
        led.next = concat(fifobus.read_data[12:5], heartbeat)

    # ----------------------------------------------------------------
    # LCD dislay
    lcd = LT24Interface()    
    resolution, color_depth = lcd.resolution, lcd.color_depth
    lcd.assign(
        lcd_on, lcd_resetn, lcd_csn, lcd_rs, lcd_wrn, lcd_rdn, lcd_data
    )

    # color bars and the interface between video source-n-sink
    vmem = VideoMemory(resolution=resolution, color_depth=color_depth)
    bar_inst = color_bars(glbl, vmem, resolution=resolution,
                      color_depth=color_depth)
    # LCD video driver
    lcd_inst = lt24lcd(glbl, vmem, lcd)

    return myhdl.instances()


# the default port map
# @todo: should be able to extact this from the board
#        definition:
#        portmap = brd.map_ports(de0nano_converters)
de0nano_converters.portmap = {
    'clock': Clock(0, frequency=50e6),
    'reset': Reset(0, active=0, async=True),
    'led': Signal(intbv(0)[8:]),
    'adc_cs_n': Signal(bool(1)),
    'adc_saddr': Signal(bool(1)),
    'adc_sdat': Signal(bool(1)),
    'adc_sclk': Signal(bool(1)),
    'i2c_sclk': Signal(bool(1)),
    'i2c_sdat': TristateSignal(bool(0)),
    'g_sensor_cs_n': Signal(bool(1)),
    'g_sensor_int': Signal(bool(1)),
    'lcd_on': Signal(bool(1)),
    'lcd_resetn': Signal(bool(1)),
    'lcd_csn': Signal(bool(1)),
    'lcd_rs': Signal(bool(1)),
    'lcd_wrn': Signal(bool(1)),
    'lcd_rdn': Signal(bool(1)),
    'lcd_data': Signal(intbv(0)[16:])
}


def build():
    global brd, flow
    brd = get_board('de0nano')
    flow = brd.get_flow(top=de0nano_converters)
    flow.run()

    
def program():
    if flow is not None:
        flow.program()


if __name__ == '__main__':
    build()
    program()
