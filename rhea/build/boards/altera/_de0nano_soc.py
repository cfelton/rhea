#
# Copyright (c) 2015 Christopher L. Felton
#
# As Per To Do, Completed GPIO pins
# Mike Kennedy (Va3TeC)
#
#

from __future__ import absolute_import

from string import Template

from rhea.build import FPGA
from rhea.build.toolflow import Quartus


class DE0NanoSOC(FPGA):
    vendor = 'altera'
    family = 'Cyclone V'
    device = '5CSEMA4U23C6'
    speed = '6'
    _name = 'de0nano_soc'

    default_clocks = {
        'clock': dict(frequency=50e6, pins=('V11',))
    }

    default_resets = {
        'reset': dict(active=0, async=True, pins=('AH16',))
    }
    
    default_ports = {
        'led': dict(pins=('W15', 'AA24', 'V16', 'V15',
                          'AF26', 'AE26', 'Y16', 'AA23',)),

        'key': dict(pins=('AH17',)),

        'sw': dict(pins=('L10', 'L9', 'H6', 'H5')),

        # bi-directional GPIO,
        'gpio': dict(pins=(
            'V12',  'AF7',  'W12',  'AF8',  'Y8',   'AB4',
            'W8',   'Y4',   'Y5',   'U11',  'T8',   'T12',
            'AH5',  'AH6',  'AH4',  'AG5',  'AH3',  'AH2',
            'AF4',  'AG6',  'AF5',  'AE4',  'T13',  'T11',
            'AE7',  'AF6',  'AF9',  'AE8',  'AD10', 'AE9',
            'AD11', 'AF10', 'AD12', 'AE11', 'AF11', 'AE12',
            'Y15',  'AG28', 'AA15', 'AH27', 'AG26', 'AH24',
            'AF23', 'AE22', 'AF21', 'AG20', 'AG19', 'AF20',
            'AC23', 'AG18', 'AH26', 'AA19', 'AG24', 'AF25',
            'AH23', 'AG23', 'AE19', 'AF18', 'AD19', 'AE20',
            'AE24', 'AD20', 'AF22', 'AH22', 'AH19', 'AH21',
            'AG21', 'AH18', 'AD23', 'AE23', 'AA18', 'AC22',)),

        # @todo: convert to an external interface
        # rxd, txd = io[0], io[1]
        # ss, mosi, miso, sck = io[10], io[11], io[12], io[13]
        # sda, scl = io[14], io[15]
        # reset_n = io[16]
        'arduino_io': dict(pins=(
            'AG13', 'AF13', 'AG10', 'AG9',
            'U14',  'U13',  'AG8',  'AH8',
            'AF17', 'AE15', 'AF15', 'AG16',
            'AH11', 'AH12', 'AH9', 'AG11', 'AH7',)),

        'adc': dict(pins=(
            'L10',  # ADC_CONVST, Conversion Start
            'L9',   # ADC_SCK, Serial DAta Clock
            'H6',   # ADC_SDI, Serial Data Input (FPGA to ADC)
            'H5'    # ADC_SDO, Serial Data Output (ADC to FPGA)
            )),
    }

    program_device_cli = (
        Template("quartus_pgm -c \"DE-SoC [1-1]\" -m jtag -o \"p;$bitfile.sof@2\" "),
             )
    # example quartus_pgm -c USB-Blaster -m jtag -o bpv:design.pof
    program_nonvolatile_cli = (Template(""),)

    def get_flow(self):
        return Quartus(brd=self)
