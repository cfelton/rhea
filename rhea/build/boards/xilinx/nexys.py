
from rhea.build import FPGA
from rhea.build.toolflow import ISE 
from rhea.build.toolflow import Vivado


class Nexys(FPGA):
    vendor = 'xilinx'
    family = 'spartan3'
    device = 'XC3S400'
    package = 'FT256'
    speed = -4
    _name = 'nexys'
    
    default_clocks = {
        'clock': dict(frequency=50e6, pins=('A8',)),
        'ifclk': dict(frequency=48e6, pins=('T9',)),
    }
    
    default_ports = {
        'led': dict(pins=('R16', 'P14', 'M13', 'N14', 
                          'L12', 'M14', 'L13', 'L14',)),
        'btn': dict(pins=('K12', 'K13', 'K14', 'J13',)),
        'sw': dict(pins=('N16', 'M15', 'M16', 'L15',
                         'K15', 'K16', 'J16', 'N15',)),
                         
        'fdio': dict(pins=('R10','M10','P10','N10',
                           'P11','N11','P12','N12',)),
                           
        'addr': dict(pins=('M7','P5')),
        
        'flaga': dict(pins=('N8')),
        'flagb': dict(pins=('P7')),
        'flagc': dict(pins=('N7')),
        'flagd': dict(pins=('T8')),
        
    }

    def get_flow(self, top=None):
        return ISE(brd=self, top=top)


class NexysVideo(FPGA):
    vendor = 'xilinx'
    family = 'artix'
    device = 'XC7A200T'
    package = 'SBG484'
    speed = -1
    _name = 'nexys'

    default_clocks = {
        'clock': dict(frequency=100e6, pins=('R4',),
                      iostandard='LVCMOS33')
    }

    default_ports = {
        'led': dict(pins=('T14', 'T15', 'T16', 'U16',
                          'V15', 'W16', 'W15', 'Y13',),
                    iostandard='LVCMOS33'),

        'sw': dict(pins=('E22', 'F21', 'G21', 'G22',
                         'H17', 'J16', 'K13', 'M17',),
                   iostandard='LVCOMS12'),

        # PMODs
        'pmod_jb': dict(pins=('V9', 'V8', 'V7', 'W7',
                              'W9', 'Y9', 'Y8', 'Y7',),
                        iostandard="LVCMOS33"),

        
    }

    def get_flow(self, top=None):
        return Vivado(brd=self, top=top)