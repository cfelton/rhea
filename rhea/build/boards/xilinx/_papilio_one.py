#
# Copyright (c) 2015 Christopher Felton
# Copyright (c) 2013 Alexander Hungenberg
#

from rhea.build import FPGA
from rhea.build.extintf._extintf import _extintf
from rhea.build.extintf._port import Port
from rhea.build.toolflow import ISE

VCCO = 'LVCMOS33'

class PapilioOne(FPGA):
    vendor = 'xilinx'
    family = 'spartan3e'
    device = 'XC3S500e'
    package = 'VQ100'
    speed = '-4'
    version = 1
    _name = 'ponev'
    
    #~ @TODO: do we need this?
    #~ no_startup_jtag_clock = True

    default_clocks = {
        'clock': dict(frequency=32e6, pins=(89,), iostandard='LVCMOS25')
    }

    default_ports = {
        'winga': dict(pins=(18, 23, 26, 33, 35, 40, 53, 57, 60, 62,
                            65, 67, 70, 79, 84, 86,), iostandard=VCCO),
        'wingb': dict(pins=(85, 83, 78, 71, 68, 66, 63, 61, 58, 54,
                            41, 36, 34, 32, 25, 22),
                      iostandard=VCCO),
        'wingc': dict(pins=(91, 92, 94, 95, 98, 2, 3, 4, 5, 9,
                            10, 11, 12, 15, 16, 17),
                      iostandard=VCCO),
        
        'jtag_tms': dict(pins=(75, ),  iostandard='LVTTL',
                    drive='8', slew='fast'),
        'jtag_tck': dict(pins=(77, ),  iostandard='LVTTL',
                    drive='8', slew='fast'),
        'jtag_tdi': dict(pins=(100,),  iostandard='LVTTL',
                    drive='8', slew='fast'),
        'jtag_tdo': dict(pins=(76, ),  iostandard='LVTTL',
                    drive='8', slew='fast'),
        'flash_cs': dict(pins=(24, ),  iostandard='LVTTL',
                    drive='8', slew='fast'),
        'flash_ck': dict(pins=(50, ),  iostandard='LVTTL',
                    drive='8', slew='fast'),
        'flash_si': dict(pins=(27, ),  iostandard='LVTTL',
                    drive='8', slew='fast'),
        'flash_so': dict(pins=(44, ),  iostandard='LVTTL',
                    drive='8', slew='fast', pullup=True),        
    }


    def get_flow(self, top=None):
        return ISE(brd=self, top=top)
