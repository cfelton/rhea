#
# Copyright (c) 2014-2015 Christopher L. Felton
# Copyright (c) 2013-2014 Jos Huisken
#

from __future__ import absolute_import

from string import Template

from rhea.build import FPGA
from rhea.build.toolflow import Quartus


class DE0Nano(FPGA):
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
        'gpio': dict(pins=(
            # JP1 (GPIO_0)
            'D3',  'C3',  'A2',  'A3',  'B3',  'B4',   #  0:5
            'A4',  'B5',  'A5',  'D5',  'B6',  'A6',   #  6:11
            'B7',  'D6',  'A7',  'C6',  'C8',  'E6',   # 12:17
            'E7',  'D8',  'E8',  'F8',  'F9',  'E9',   # 18:23
            'C9',  'D9',  'E11', 'E10', 'C11', 'B11',  # 24:29
            'A12', 'D11', 'D11', 'D12', 'B12',         # 30:32
            # JP2 (GPIO_1)
            'F13', 'T15', 'T14', 'T13', 'R13', 'T12',  #  0:5 
            'R12', 'T11', 'T10', 'R11', 'P11', 'R10',  #  6:11
            'N12', 'P9',  'N9',  'N11', 'L16', 'K16',  # 12:17
            'R16', 'L15', 'P15', 'P16', 'R14', 'N16',  # 18:23
            'N15', 'P14', 'L14', 'N14', 'M10', 'L13',  # 24:29
            'J16', 'K15', 'J13', 'J14'                 # 30:32
        ), iostandard='3.3-V LVTTL'),

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

        # LT24 pins 
        # @todo: use an extintf interface/object
        'lcd_on': dict(pins=('J14',)),
        'lcd_resetn': dict(pins=('K15',)),
        'lcd_csn': dict(pins=('N16',)),
        'lcd_rs': dict(pins=('P11',)),
        'lcd_wrn': dict(pins=('R11',)),
        'lcd_rdn': dict(pins=('T10',)),
        'lcd_data': dict(pins=('R12', 'T12', 'R13', 'T13',
                               'R10', 'N12', 'P9',  'N9',
                               'N11', 'L16', 'K16', 'R16',
                               'L15', 'P15', 'P16', 'R14',))
    }

    program_device_cli = (
        Template("quartus_pgm -c USB-Blaster -m jtag -o \"p;$bitfile.sof\" "),
             )
    # example quartus_pgm -c USB-Blaster -m jtag -o bpv:design.pof
    program_nonvolatile_cli = (Template(""),)
    
    def get_flow(self, top=None):
        return Quartus(brd=self, top=top)