
from rhea.build import FPGA
from rhea.build.toolflow import ISE 


class XUPV2P(FPGA):
    vendor = 'xilinx'
    family = 'virtex2p'
    device = 'XC2VP30'
    package = 'ff896'
    speed = -7
    _name = 'xupv2p'
    
    default_clocks = {
        'clock': dict(frequency=100e6, pins=('AJ15',)),
    }
    
    default_resets = {
        'reset': dict(active=0, async=True, pins=('AH5',)),    
    }
    
    default_ports = {
        'led': dict(pins=('AC4','AC3','AA6','AA5',)),
    }

    def get_flow(self, top=None):
        return ISE(brd=self, top=top)