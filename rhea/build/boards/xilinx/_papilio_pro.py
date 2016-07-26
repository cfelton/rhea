#
# Copyright (c) 2015 Christopher Felton, Felix Vietmeyer
#

from myhdl import TristateSignal, intbv

from rhea.build import FPGA
from rhea.build.extintf import Port
from rhea.build.toolflow import ISE

VCCO = 'LVCMOS33'

class PapilioPro(FPGA):
    vendor = 'xilinx'
    family = 'spartan6'
    device = 'XC6SLX9'
    package = 'TQG144'
    speed = '-2'
    version = 1
    _name = 'pprov'
    no_startup_jtag_clock = True
    
    default_clocks = {
        'clock': dict(frequency=32e6, pins=(94,),
                    iostandard='LVTTL')        
    }
    
    default_ports = {
        'winga': dict(pins=(48, 51, 56, 58, 61, 66, 67, 75, 79, 81, 83,
                    85, 88, 93, 98, 100), iostandard=VCCO),
        'wingb': dict(pins=(99, 97, 92, 87, 84, 82, 80, 78, 74, 95, 62,
                    59, 57, 55, 50, 47),  iostandard=VCCO),
        'wingc': dict(pins=(114, 115, 116, 117, 118, 119, 120, 121, 123,
                    124, 126, 127, 131, 132, 133, 134), 
                    iostandard=VCCO),
        
        'jtag_tms': dict(pins=(75, ),  iostandard='LVTTL',
                    drive='8', slew='fast'),
        'jtag_tck': dict(pins=(77, ),  iostandard='LVTTL',
                    drive='8', slew='fast'),
        'jtag_tdi': dict(pins=(100,),  iostandard='LVTTL',
                    drive='8', slew='fast'),
        'jtag_tdo': dict(pins=(76, ),  iostandard='LVTTL',
                    drive='8', slew='fast'),
        
        #TODO: Is the pullup needed?
        'flash_cs': dict(pins=(38, ),  iostandard='LVTTL',
                    drive='8', slew='fast'),
        'flash_ck': dict(pins=(70, ),  iostandard='LVTTL',
                    drive='8', slew='fast'),
        'flash_si': dict(pins=(64, ),  iostandard='LVTTL',
                    drive='8', slew='fast'),
        'flash_so': dict(pins=(65, ),  iostandard='LVTTL',
                    drive='8', slew='fast', pullup=True),
        
        'tx': dict(pins=(105,), iostandard='LVTTL'),
        'rx': dict(pins=(101,), iostandard='LVTTL'),
        
        'sdram_addr': dict(pins=(140, 139, 138, 137, 46, 45, 44, 43, 41,
                    40, 141, 35, 34), iostandard='LVTTL'),
        'sdram_data': dict(pins=(9, 10, 11, 12, 14, 15, 16, 8, 21, 22,
                    23, 24, 26, 27, 29, 30), iostandard='LVTTL'),
        'sdram_dqml': dict(pins=(7, ),  iostandard='LVTTL'),
        'sdram_dqmh': dict(pins=(17, ),  iostandard='LVTTL'),
        'sdram_ba': dict(pins=(143, 142),  iostandard='LVTTL'),
        'sdram_nwe': dict(pins=(6, ),  iostandard='LVTTL'),
        'sdram_ncas': dict(pins=(5, ),  iostandard='LVTTL'),
        'sdram_nras': dict(pins=(2, ),  iostandard='LVTTL'),
        'sdram_cs': dict(pins=(1, ),  iostandard='LVTTL'),
        'sdram_clk': dict(pins=(32, ),  iostandard='LVTTL'),
        'sdram_cke': dict(pins=(33, ),  iostandard='LVTTL'),
    }

    def get_flow(self, top=None):
        return ISE(brd=self, top=top)
