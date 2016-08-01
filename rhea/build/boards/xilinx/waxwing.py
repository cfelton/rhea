#
# Copyright (c) 2016 Felix Vietmeyer
#

from myhdl import TristateSignal, intbv

from rhea.build import FPGA
from rhea.build.extintf import Port
from rhea.build.toolflow import ISE

VCCO = 'LVCMOS33'

class Waxwing45(FPGA):
    """ Waxwing mini module with Spartan-6 LX45
    """
    vendor = 'xilinx'
    family = 'spartan6'
    device = 'XC6SLX45'
    package = 'CSG324'
    speed = '-2'
    version = 1
    _name = 'waxwing'
    no_startup_jtag_clock = True
    
    default_clocks = {
        'clock': dict(frequency=100e6, pins=('V10',),
                    iostandard='LVCMOS33')        
    }
    
    default_ports = {
        #P1 pins mapped are
        #9, 11, 13-18, 21-34, 37-52, 55-70, 73-82
        'p1': dict(pins=('R3', 'T3',                    #9, 11
                    'T4', 'R5', 'V4', 'T5', 'R7', 'T6', #13-18
                    'T7', 'V6', 'U5', 'P7', 'V5', 'N6', 'V7', 'N7',
                    'U7', 'P8', 'V8', 'N8', 'U8', 'M8', #21-34
                    'R8', 'R11', 'T8', 'T11', 'T9', 'R10', 'V9', 'T10',
                    'N10', 'M14', 'P11', 'N14', 'L12', 'T12', 'L13',
                    'V12',                              #37-52
                    'N11', 'N15', 'M11', 'N16', 'T14', 'P15', 'V14',
                    'P16', 'N18', 'U17', 'N17', 'U18', 'V11', 'M18',
                    'U11', 'M16',                       #55-70
                    'V13', 'P18', 'U13', 'P17', 'V15', 'V16', 'U15',
                    'U16', 'T17', 'T18'                 #73-82
                    ), iostandard=VCCO),
        
        #P2 pins mapped are
        #6, 8-16, 19-34, 37-52, 55-70, 73-84
        'p2': dict(pins=('B2',                          #6
                    'A2', 'D8', 'B3', 'C8', 'A3', 'D6', 'C5', 'C6',
                    'A5'                                #8-16
                    'B6', 'B4', 'A6', 'A4', 'D11', 'C7', 'C11', 'A7',
                    'B8', 'D9', 'A8', 'C9', 'H16', 'B9', 'H15',
                    'A9',                               #19-34
                    'C10', 'C13', 'A10', 'A13', 'C14', 'F9', 'D14',
                    'G9', 'F13', 'C15', 'E13', 'A15', 'F15', 'B11',
                    'F16', 'A11',                       #37-52
                    'E16', 'B12', 'E18', 'A12', 'B16', 'B14', 'A16',
                    'A14', 'D17', 'F14', 'D18', 'G14', 'H13', 'C17',
                    'H14', 'C18',                       #55-70
                    'G16', 'L17', 'G18', 'L18', 'K12', 'F18', 'K13',
                    'F17', 'L15', 'L14', 'L16', 'M13'   #73-84
                    ),  iostandard=VCCO),
        
        #JTAG intf
        'jtag_tms': dict(pins=('B18', ),  iostandard='LVTTL',
                    drive='8', slew='fast'),
        'jtag_tck': dict(pins=('A17', ),  iostandard='LVTTL',
                    drive='8', slew='fast'),
        'jtag_tdi': dict(pins=('D15',),  iostandard='LVTTL',
                    drive='8', slew='fast'),
        'jtag_tdo': dict(pins=('D16', ),  iostandard='LVTTL',
                    drive='8', slew='fast'),
        
        #TODO: Is the pullup needed?
        #Flash  -   W25Q128FV
        'spi_cs': dict(pins=('V3', ),  iostandard='LVTTL',
                    drive='8', slew='fast'),
        'spi_sck': dict(pins=('R15', ),  iostandard='LVTTL',
                    drive='8', slew='fast'),
        'spi_sdi': dict(pins=('T13', ),  iostandard='LVTTL',
                    drive='8', slew='fast'),
        'spi_sdo': dict(pins=('R13', ),  iostandard='LVTTL',
                    drive='8', slew='fast', pullup=True),
        
        #sdram  -   MT46H32M16LF / W949D6CBHX6E
        'ddr_d': dict(pins=('L2', 'L1', 'K2', 'K1', 'H2', 'H1', 'J3',
                    'J1', 'M3', 'M1', 'N2', 'N1', 'T2', 'T1', 'U2',
                    'U1'), iostandard='MOBILE_DDR'),
        'ddr_a': dict(pins=('J7', 'J6', 'H5', 'L7', 'F3', 'H4', 'H3',
                    'H6', 'D2', 'D1', 'F4', 'D3', 'G6'),
                    iostandard='MOBILE_DDR'),
        'ddr_uqds': dict(pins=('P2', ),  iostandard='MOBILE_DDR'),
        'ddr_lqds': dict(pins=('L4', ),  iostandard='MOBILE_DDR'),
        'ddr_udm': dict(pins=('K4', ),  iostandard='MOBILE_DDR'),
        'ddr_ldm': dict(pins=('K3', ),  iostandard='MOBILE_DDR'),
        'ddr_ras': dict(pins=('L5', ),  iostandard='MOBILE_DDR'),
        'ddr_cas': dict(pins=('K5', ),  iostandard='MOBILE_DDR'),
        'ddr_ck': dict(pins=('G3', ),  iostandard='DIFF_MOBILE_DDR'),
        'ddr_ck_n': dict(pins=('G1', ),  iostandard='DIFF_MOBILE_DDR'),
        'ddr_ba': dict(pins=('F2', 'F1'),  iostandard='MOBILE_DDR'),
        'ddr_we': dict(pins=('E3', ),  iostandard='MOBILE_DDR'),
        'ddr_cke': dict(pins=('H7', ),  iostandard='MOBILE_DDR'),
    }

    def get_flow(self, top=None):
        return ISE(brd=self, top=top)

class Waxwing45carrier(FPGA):
    """ Waxwing module on carrier with Spartan-6 LX45
    """
    vendor = 'xilinx'
    family = 'spartan6'
    device = 'XC6SLX45'
    package = 'CSG324'
    speed = '-2'
    version = 1
    _name = 'waxwing'
    no_startup_jtag_clock = True
    
    default_clocks = {
        'clock': dict(frequency=100e6, pins=('V10',),
                    iostandard='LVCMOS33')        
    }
    
    default_ports = {
        #P3 pins mapped are
        #13-28, 33-48, 53-72
        'p3': dict(pins=('U16', 'V16', 'T18', 'T17', 'P17', 'P18',
                    'V15', 'U15', 'M16', 'M18', 'V13', 'U13', 'U18',
                    'U17', 'V11', 'U11',                #13-28
                    'P15', 'P16', 'N18', 'N17', 'N15', 'N16', 'T14',
                    'V14', 'T12', 'V12', 'N11', 'M11', 'M14', 'N14',
                    'L12', 'L13',                       #33-48
                    'R10', 'T10', 'N10', 'P11', 'R11', 'T11', 'V8',
                    'U8', 'N8', 'M8', 'V7', 'U7', 'V6', 'T6', 'N7',
                    'P8', 'T5', 'R5', 'P7', 'N6'        #53-72
                    ), iostandard=VCCO),
        
        #P4 pins mapped are
        #7-28, 33-48, 53-72
        'p4': dict(pins=('V9', 'T9', 'T8', 'R8', 'F18', 'F17', 'B14',
                    'A14', 'C18', 'C17', 'L14', 'M13', 'L15', 'L16',
                    'L17', 'L18', 'K12', 'K13', 'F15', 'F16', 'G16',
                    'G18',                              #7-28
                    'F14', 'G14', 'H14', 'H13', 'B12', 'A12', 'D17',
                    'D18', 'C15', 'A15', 'B16', 'A16', 'C13', 'A13',
                    'E16', 'E18',                       #33-48
                    'C9', 'D9', 'F13', 'E13', 'A11', 'B11', 'C14',
                    'D14', 'G9', 'F9', 'C10', 'A10', 'A9', 'B9', 'H16',
                    'H15', 'A7', 'C7', 'B8', 'A8'       #53-72
                    ),  iostandard=VCCO),
        
        #P5 pins mapped are
        #1-8
        'p5': dict(pins=('V4', 'T4', 'T3', 'R3', 'R7', 'T7', 'U5', 'V5'
                    ),  iostandard=VCCO),
        
        #P6 pins mapped are
        #1-8
        'p6': dict(pins=('A4', 'B4', 'A5', 'C5', 'A3', 'B3', 'A2', 'B2'
                    ),  iostandard=VCCO),
                    
        #P7 pins mapped are
        #1-8
        'p7': dict(pins=('C8', 'D8', 'C6', 'D6', 'A6', 'B6', 'C11',
                    'D11'),  iostandard=VCCO),
        
        #JTAG intf
        'jtag_tms': dict(pins=('B18', ),  iostandard='LVTTL',
                    drive='8', slew='fast'),
        'jtag_tck': dict(pins=('A17', ),  iostandard='LVTTL',
                    drive='8', slew='fast'),
        'jtag_tdi': dict(pins=('D15',),  iostandard='LVTTL',
                    drive='8', slew='fast'),
        'jtag_tdo': dict(pins=('D16', ),  iostandard='LVTTL',
                    drive='8', slew='fast'),
        
        #TODO: Is the pullup needed?
        #Flash  -   W25Q128FV
        'spi_cs': dict(pins=('V3', ),  iostandard='LVTTL',
                    drive='8', slew='fast'),
        'spi_sck': dict(pins=('R15', ),  iostandard='LVTTL',
                    drive='8', slew='fast'),
        'spi_sdi': dict(pins=('T13', ),  iostandard='LVTTL',
                    drive='8', slew='fast'),
        'spi_sdo': dict(pins=('R13', ),  iostandard='LVTTL',
                    drive='8', slew='fast', pullup=True),
        
        #sdram  -   MT46H32M16LF / W949D6CBHX6E
        'ddr_d': dict(pins=('L2', 'L1', 'K2', 'K1', 'H2', 'H1', 'J3',
                    'J1', 'M3', 'M1', 'N2', 'N1', 'T2', 'T1', 'U2',
                    'U1'), iostandard='MOBILE_DDR'),
        'ddr_a': dict(pins=('J7', 'J6', 'H5', 'L7', 'F3', 'H4', 'H3',
                    'H6', 'D2', 'D1', 'F4', 'D3', 'G6'),
                    iostandard='MOBILE_DDR'),
        'ddr_uqds': dict(pins=('P2', ),  iostandard='MOBILE_DDR'),
        'ddr_lqds': dict(pins=('L4', ),  iostandard='MOBILE_DDR'),
        'ddr_udm': dict(pins=('K4', ),  iostandard='MOBILE_DDR'),
        'ddr_ldm': dict(pins=('K3', ),  iostandard='MOBILE_DDR'),
        'ddr_ras': dict(pins=('L5', ),  iostandard='MOBILE_DDR'),
        'ddr_cas': dict(pins=('K5', ),  iostandard='MOBILE_DDR'),
        'ddr_ck': dict(pins=('G3', ),  iostandard='DIFF_MOBILE_DDR'),
        'ddr_ck_n': dict(pins=('G1', ),  iostandard='DIFF_MOBILE_DDR'),
        'ddr_ba': dict(pins=('F2', 'F1'),  iostandard='MOBILE_DDR'),
        'ddr_we': dict(pins=('E3', ),  iostandard='MOBILE_DDR'),
        'ddr_cke': dict(pins=('H7', ),  iostandard='MOBILE_DDR'),
    }

    def get_flow(self, top=None):
        return ISE(brd=self, top=top)
