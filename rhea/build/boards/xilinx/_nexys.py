
from ..._fpga import _fpga
from ...toolflow import ISE 

class Nexys(_fpga):
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