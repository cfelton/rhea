#
# Copyright (c) 2014-2015 Christopher L. Felton
# Copyright (c) 2013-2014 Jos Huisken
#

from __future__ import absolute_import

from string import Template

from ..._fpga import _fpga
from ...toolflow import Quartus


class DE0Nano(_fpga):
    vendor = 'altera'
    family = 'Cyclone IV E'
    device = 'EP4CE22F17C6'
    speed = '6'
    _name = 'de0nano'

    default_clocks = {
        'clock': dict(frequency=50e6, pins=('R8',))
    }

    default_resets = {
        'reset': dict(active=0, async=True, pins=('J15',))
    }
    
    default_ports = {
        'led': dict(pins=('L3', 'B1', 'F3', 'D1',
                          'A11', 'B13', 'A13', 'A15',)),
        'key': dict(pins=('E1', 'J15')),
        'dip': dict(pins=('M1', 'T8', 'B9', 'M15')),
        
        # bi-directional GPIO, naming slightly different than the
        # reference manual and schematics.  The GPIO are not separated
        # into GPIO_0 and GPIO_1
        # @todo: finish the GPIO pins
        'gpio': dict(pins=('D3', 'C3', 'A2', 'A3', 'B3', 'B4',
                           'A4', 'B5', 'A5', 'D5', 'B6', 'A6')),

        # ADC pins (names given in the user manula)
        'adc_cs_n': dict(pins=('A10',)),
        'adc_saddr': dict(pins=('B10',)),
        'adc_sdat': dict(pins=('A9',)),
        'adc_sclk': dict(pins=('B14',)),

        # I2C lines shared with accelerometer and EEPROM
        'i2c_sclk': dict(pins=('F2',)),
        'i2c_sdat': dict(pins=('F1',)),
        'g_sensor_cs_n': dict(pins=('G5',)),
        'g_sensor_int': dict(pins=('M2',)),
    }

    program_device_cli = (
        Template("quartus_pgm -c USB-Blaster -m jtag -o \"p;$bitfile.sof\" "),
             )
    # example quartus_pgm -c USB-Blaster -m jtag -o bpv:design.pof
    program_nonvolatile_cli = (Template(""),)
    
    def get_flow(self, top=None):
        return Quartus(brd=self, top=top)