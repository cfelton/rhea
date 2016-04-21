#
# Copyright (c) 2015 Christopher L. Felton
#
# 
# Added Support for the Terasic De1-SoC Board
# By Mike Kennedy (Va3TeC)
#

from __future__ import absolute_import

from string import Template

from rhea.build import FPGA
from rhea.build.toolflow import Quartus


class DE1SOC(FPGA):
    vendor = 'altera'
    family = 'Cyclone V'
    device = '5CSEMA5F31C6'
    speed = '6'
    _name = 'de1_soc'
    revision = 'F'

    # As Per page 23 of the user Guide for DE1-SoC
    default_clocks = {
        'clock': dict(frequency=50e6, pins=('AF14',)),
        'clock2': dict(frequency=50e6, pins=('AA16',)),
        'clock3': dict(frequency=50e6, pins=('Y26',)),
        'clock4': dict(frequency=50e6, pins=('K14',)),
    }

    default_resets = {
        # if an external reset is desired push button 0 (key0)
        # can be used.  Note this overlaps with "key[0]"
        'reset': dict(active=0, async=True, pins=('AA14',))
    }
    
    default_ports = {
        'led': dict(pins=('V16', 'W16', 'V17', 'V18', 'W17',
                          'W19', 'Y19', 'W20', 'W21', 'Y21')),

        'key': dict(pins=('AA14', 'AA15', 'W15', 'Y16')),

        'sw': dict(pins=('AB12', 'AC12', 'AF9', 'AF10',
                         'AD11', 'AD12', 'AE11', 'AC9',
                         'AD10', 'AE12')),

        'hex0': dict(pins=('AE26', 'AE27', 'AE28', 'AG27',  # HEX0-HEX3
                           'AF28', 'AG28', 'AH28', )),      # HEX4-HEX6

        'hex1': dict(pins=('AJ29', 'AH29', 'AH30', 'AG30',
                           'AF29', 'AF30', 'AD27',)),

        'hex2': dict(pins=('AB23', 'AE29', 'AD29', 'AC28',
                           'AD30', 'AC29', 'AC30',)),

        'hex3': dict(pins=('AD26', 'AC27', 'AD25', 'AC25',
                           'AB28', 'AB25', 'AB22',)),

        'hex4': dict(pins=('AA24', 'Y23', 'Y24', 'W22',
                           'W24', 'V23', 'W25', )),

        'hex5': dict(pins=('V25', 'AA28', 'Y27', 'AB27',
                           'AB26', 'AA26', 'AA25',)),

        # bi-directional GPIO, 
        # @todo: finish the GPIO pins
        'gpio': dict(pins=(
            'AC18', 'Y17',  'AD17', 'Y18',  'AK16', 'AK18',
            'AK19', 'AJ19', 'AJ17', 'AJ16', 'AH18', 'AH17',
            'AG16', 'AE16', 'AF16', 'AG17', 'AA18', 'AA19',
            'AE17', 'AC20', 'AH19', 'AJ20', 'AH20', 'AK21',
            'AD19', 'AD20', 'AE18', 'AE19', 'AF20', 'AF21',
            'AF19', 'AG21', 'AF18', 'AG20', 'AG18', 'AJ21',
            'AB17', 'AA21', 'AB21', 'AC23', 'AD24', 'AE23',
            'AE24', 'AF25', 'AF26', 'AG25', 'AG26', 'AH24',
            'AH27', 'AJ27', 'AK29', 'AK28', 'AK27', 'AJ26',
            'AK26', 'AH25', 'AJ25', 'AJ24', 'AK24', 'AG23',
            'AK23', 'AH23', 'AK22', 'AJ22', 'AH22', 'AG22',
            'AF24', 'AF23', 'AE22', 'AD21', 'AA20', 'AC22',)),

        # ADC pins (names given in the user manula)
        # 'adc_cs_n': dict(pins=('A10',)),
        # 'adc_saddr': dict(pins=('B10',)),
        # 'adc_sdat': dict(pins=('A9',)),
        # 'adc_sclk': dict(pins=('B14',)),

        # I2C lines shared with accelerometer and EEPROM
        # 'i2c_sclk': dict(pins=('F2',)),
        # 'i2c_sdat': dict(pins=('F1',)),
        # 'g_sensor_cs_n': dict(pins=('G5',)),
        # 'g_sensor_int': dict(pins=('M2',)),

        # LT24 pins 
        # @todo: use an extintf interface/object DE1_SOC Board
        'lcd_on': dict(pins=('AC22',)),          # GPIO 1 pin
        'lcd_resetn': dict(pins=('AD21',)),	     # GPIO 1 pin
        'lcd_csn': dict(pins=('AA20',)),         # GPIO 1 pin
        'lcd_rs': dict(pins=('AH27',)),	         # GPIO 1 pin
        'lcd_wrn': dict(pins=('AH24',)),         # GPIO 1 pin
        'lcd_rdn': dict(pins=('AG26',)),         # GPIO 1 pin
        'lcd_data': dict(pins=(
            'AF26', 'AF25', 'AE24', 'AE23',		 # GPIO 1, Data 0:3
            'AJ27', 'AK29', 'AK28',  'AK27',	 # GPIO 1, Data 4:7
            'AJ26', 'AK26', 'AH25', 'AJ25',		 # GPIO 1, DAta 8:11
            'AJ24', 'AK24', 'AG23', 'AK23',)),	 # GPIO 1, DAta 12:15

        # VGA Pins added for the On board VGA DAC chip. ADV7123
        # triple 10 Bit High speed Video DAC by analog devices.
        # The names are the same as the user manual but lowercase.
        # Red Data
        'vga_r': dict(pins=('A13', 'C13', 'E13', 'B12',        # Data 0:3
                            'C12', 'D12', 'E12',  'F13',)),    # Data 4:7

        # Green Data
        'vga_g': dict(pins=('J9', 'J10', 'H12', 'G10',         # Data 0:3
                            'G11', 'G12', 'F11',  'E11', )),   # Data 4:7

        # Blue
        'vga_b': dict(pins=('B13', 'G13', 'H13', 'F14',        # Data 0:3
                            'H14', 'F15', 'G15',  'J14', )),   # Data 4:7

        'vga_clk': dict(pins=('A11',)),
        'vga_sync_n': dict(pins=('C10',)),
        'vga_blank_n': dict(pins=('F10',)),
        'vga_vs': dict(pins=('D11',)),
        'vga_hs': dict(pins=('B11',)),
    }

    program_device_cli = (
        Template(
            "quartus_pgm -c \"DE-SoC [1-1]\" -m jtag -o \"p;$bitfile.sof@2\" "),
    )
    # example quartus_pgm -c USB-Blaster -m jtag -o bpv:design.pof
    program_nonvolatile_cli = (Template(""),)

    def get_flow(self, top=None):
        return Quartus(brd=self, top=top)
