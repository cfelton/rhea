#
# Copyright (c) 2015 Christopher Felton, Felix Vietmeyer
#

from myhdl import TristateSignal, intbv

from rhea.build import FPGA
from rhea.build.extintf import Port
from rhea.build.toolflow import ISE


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
        'wingA': dict(pins=(48, 51, 56, 58, 61, 66, 67, 75, 79, 81, 83,
                    85, 88, 93, 98, 100), iostandard=VCCO),
        'wingB': dict(pins=(99, 97, 92, 87, 84, 82, 80, 78, 74, 95, 62,
                    59, 57, 55, 50, 47),  iostandard=VCCO),
        'wingC': dict(pins=(114, 115, 116, 117, 118, 119, 120, 121, 123,
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
        
        'tx': dict(pins=(P105,), iostandard='LVTTL'),
        'rx': dict(pins=(P101,), iostandard='LVTTL'),
        
        #TODO: What about pins for SDRAM?
        #~ NET SDRAM_ADDR(0)  LOC="P140" | IOSTANDARD=LVTTL;                                # SDRAM_ADDR0
        #~ NET SDRAM_ADDR(1)  LOC="P139" | IOSTANDARD=LVTTL;                                # SDRAM_ADDR1
        #~ NET SDRAM_ADDR(2)  LOC="P138" | IOSTANDARD=LVTTL;                                # SDRAM_ADDR2
        #~ NET SDRAM_ADDR(3)  LOC="P137" | IOSTANDARD=LVTTL;                                # SDRAM_ADDR3
        #~ NET SDRAM_ADDR(4)  LOC="P46"  | IOSTANDARD=LVTTL;                                # SDRAM_ADDR4
        #~ NET SDRAM_ADDR(5)  LOC="P45"  | IOSTANDARD=LVTTL;                                # SDRAM_ADDR5
        #~ NET SDRAM_ADDR(6)  LOC="P44"  | IOSTANDARD=LVTTL;                                # SDRAM_ADDR6
        #~ NET SDRAM_ADDR(7)  LOC="P43"  | IOSTANDARD=LVTTL;                                # SDRAM_ADDR7
        #~ NET SDRAM_ADDR(8)  LOC="P41"  | IOSTANDARD=LVTTL;                                # SDRAM_ADDR8
        #~ NET SDRAM_ADDR(9)  LOC="P40"  | IOSTANDARD=LVTTL;                                # SDRAM_ADDR9
        #~ NET SDRAM_ADDR(10) LOC="P141" | IOSTANDARD=LVTTL;                                # SDRAM_ADDR10
        #~ NET SDRAM_ADDR(11) LOC="P35"  | IOSTANDARD=LVTTL;                                # SDRAM_ADDR11
        #~ NET SDRAM_ADDR(12) LOC="P34"  | IOSTANDARD=LVTTL;                                # SDRAM_ADDR12
        #~ NET SDRAM_DATA(0)  LOC="P9"   | IOSTANDARD=LVTTL;                                # SDRAM_DATA0
        #~ NET SDRAM_DATA(1)  LOC="P10"  | IOSTANDARD=LVTTL;                                # SDRAM_DATA1
        #~ NET SDRAM_DATA(2)  LOC="P11"  | IOSTANDARD=LVTTL;                                # SDRAM_DATA2
        #~ NET SDRAM_DATA(3)  LOC="P12"  | IOSTANDARD=LVTTL;                                # SDRAM_DATA3
        #~ NET SDRAM_DATA(4)  LOC="P14"  | IOSTANDARD=LVTTL;                                # SDRAM_DATA4
        #~ NET SDRAM_DATA(5)  LOC="P15"  | IOSTANDARD=LVTTL;                                # SDRAM_DATA5
        #~ NET SDRAM_DATA(6)  LOC="P16"  | IOSTANDARD=LVTTL;                                # SDRAM_DATA6
        #~ NET SDRAM_DATA(7)  LOC="P8"   | IOSTANDARD=LVTTL;                                # SDRAM_DATA7
        #~ NET SDRAM_DATA(8)  LOC="P21"  | IOSTANDARD=LVTTL;                                # SDRAM_DATA8
        #~ NET SDRAM_DATA(9)  LOC="P22"  | IOSTANDARD=LVTTL;                                # SDRAM_DATA9
        #~ NET SDRAM_DATA(10) LOC="P23"  | IOSTANDARD=LVTTL;                                # SDRAM_DATA10
        #~ NET SDRAM_DATA(11) LOC="P24"  | IOSTANDARD=LVTTL;                                # SDRAM_DATA11
        #~ NET SDRAM_DATA(12) LOC="P26"  | IOSTANDARD=LVTTL;                                # SDRAM_DATA12
        #~ NET SDRAM_DATA(13) LOC="P27"  | IOSTANDARD=LVTTL;                                # SDRAM_DATA13
        #~ NET SDRAM_DATA(14) LOC="P29"  | IOSTANDARD=LVTTL;                                # SDRAM_DATA14
        #~ NET SDRAM_DATA(15) LOC="P30"  | IOSTANDARD=LVTTL;                                # SDRAM_DATA15
        #~ NET SDRAM_DQML     LOC="P7"   | IOSTANDARD=LVTTL;                                # SDRAM_DQML
        #~ NET SDRAM_DQMH     LOC="P17"  | IOSTANDARD=LVTTL;                                # SDRAM_DQMH
        #~ NET SDRAM_BA(0)    LOC="P143" | IOSTANDARD=LVTTL;                                # SDRAM_BA0
        #~ NET SDRAM_BA(1)    LOC="P142" | IOSTANDARD=LVTTL;                                # SDRAM_BA1
        #~ NET SDRAM_nWE      LOC="P6"   | IOSTANDARD=LVTTL;                                # SDRAM_nWE
        #~ NET SDRAM_nCAS     LOC="P5"   | IOSTANDARD=LVTTL;                                # SDRAM_nCAS
        #~ NET SDRAM_nRAS     LOC="P2"   | IOSTANDARD=LVTTL;                                # SDRAM_nRAS
        #~ NET SDRAM_CS       LOC="P1"   | IOSTANDARD=LVTTL;                                # SDRAM_CS
        #~ NET SDRAM_CLK      LOC="P32"  | IOSTANDARD=LVTTL;                                # SDRAM_CLK
        #~ NET SDRAM_CKE      LOC="P33"  | IOSTANDARD=LVTTL;                                # SDRAM_CKE
    }

    def get_flow(self, top=None):
        return ISE(brd=self, top=top)
