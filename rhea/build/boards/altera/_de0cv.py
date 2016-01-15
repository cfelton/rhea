#
# Copyright (c) 2014-2015 Christopher L. Felton
# Copyright (c) 2013-2014 Jos Huisken
#

from __future__ import absolute_import

from string import Template

from rhea.build import FPGA
from rhea.build.toolflow import Quartus


class DE0CV(FPGA):
    vendor = 'altera'
    family = 'Cyclone V'
    device = '5CEBA4F23C7'
    speed = '6'
    _name = 'de0cv'

    default_clocks = {
        'clock': dict(frequency=50e6, pins=('M9',)),
        'clock2': dict(frequency=50e6, pins=('H13',)),
        'clock3': dict(frequency=50e6, pins=('E10',)),
        'clock4': dict(frequency=50e6, pins=('V15',))
    }

    default_resets = {
        'reset': dict(active=0, async=True, pins=('P22',))
    }

    default_ports = {
        'key': dict(pins=('U7', 'W9','M7','M6')),
        'sw': dict(pins=('U13', 'V13', 'T13', 'I12', 'AA15',
                         'AB15', 'AA14', 'AA13', 'AB13', 'AB12')),
        # bi-directional GPIO, naming slightly different than the
        # reference manual and schematics.  The GPIO are not separated
        # into GPIO_0 and GPIO_1
        'gpio': dict(pins=(
            # GPIO_0
            'N16', 'B16', 'M16', 'C16', 'D17', 'K20',  #  0:5
            'K21', 'K22', 'M20', 'M21', 'N21', 'R22',  #  6:11
            'R21', 'T22', 'N20', 'N19', 'M22', 'P19',  # 12:17
            'L22', 'P17', 'P16', 'M18', 'L18', 'L17',  # 18:23
            'L19', 'K17', 'K19', 'P18', 'R15', 'R17',  # 24:29
            'R16', 'T20', 'T19', 'T18', 'T17', 'T15'   # 30:35
            # GPIO_1 
            'H16', 'A12', 'H15', 'B12', 'A13', 'B13',  #  0:5
            'C13', 'D13', 'G18', 'G17', 'H18', 'J18',  #  6:11
            'J19', 'G11', 'H10', 'J11', 'H14', 'A15',  # 12:17
            'J13',  'L8', 'A14', 'B15', 'C15', 'E14',  # 18:23
            'E15', 'E16', 'F14', 'F15', 'F13', 'F12',  # 24:29
            'G16', 'G15', 'G13', 'G12', 'J17', 'K16'   # 30:35
            ), iostandard='3.3-V LVTTL'),
        'hex0': dict(pins=(
            'U21', 'V21', 'W22', 'W21', 'Y22', 'Y21', 'AA22'
            ), iostandard='3.3-V LVTTL'),
        'hex1': dict(pins=(
            'AA20', 'AB20', 'AA19', 'AA18', 'AB18', 'AA17', 'U22'
            ), iostandard='3.3-V LVTTL'),
        'hex2': dict(pins=(
            'Y19', 'AB17', 'AA10', 'Y14', 'V14', 'AB22', 'AB21'
            ), iostandard='3.3-V LVTTL'),
        'hex3': dict(pins=(
            'Y16', 'W16', 'Y17', 'V16', 'U17', 'V18', 'V19'
            ), iostandard='3.3-V LVTTL'),
        'hex4': dict(pins=(
            'U20', 'Y20', 'V20', 'U16', 'U15', 'Y15', 'P9'
            ), iostandard='3.3-V LVTTL'),
        'hex5': dict(pins=(
            'N9', 'M8', 'T14', 'P14', 'C1', 'C2', 'W19'
            ), iostandard='3.3-V LVTTL'),
        'ledr': dict(pins=(
            'AA2', 'AA1', 'W2', 'Y3', 'N2', 'N1', 'U2', 'U1', 'L2', 'L1'
            ), iostandard='3.3-V LVTTL'),
        'ps2_clk': dict(pins=('D3',)),
        'ps2_clk2': dict(pins=('E2',)),
        'ps2_dat': dict(pins=('G2',)),
        'ps2_dat2': dict(pins=('G1',)),
        'sd_clk': dict(pins=('H11',)),
        'sd_cmd': dict(pins=('B11',)),
        'sd_data': dict(pins=('K9', 'D12', 'E12', 'C11',))
    }

    program_device_cli = (
        Template("quartus_pgm -c USB-Blaster -m jtag -o \"p;$bitfile.sof\" "),
             )
    # example quartus_pgm -c USB-Blaster -m jtag -o bpv:design.pof
    program_nonvolatile_cli = (Template(""),)
 
    def get_flow(self, top=None):
        return Quartus(brd=self, top=top)
