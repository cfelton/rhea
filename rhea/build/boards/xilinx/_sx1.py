from ..._fpga import _fpga
from ...toolflow import ISE 

class SX1(_fpga):
    vendor = 'xilinx'
    family = 'spartan3e'
    device = 'XC3S500E'
    package = 'vq100'
    speed = -5
    _name = 'sx1'
    
    default_clocks = {
        'clock': dict(frequency=48e6, pins=(35,)),
    }
    
    default_resets = {
        'reset': dict(active=0, async=True, pins=(13,)),    
    }
    
    default_ports = {
        'led': dict(pins=(90, 91, 92, 94, 95, 96, 99)),
                         
        # FX2 connection
        'fdio': dict(pins=(0, 0, 0, 0, 0, 0, 0, 0)),
        'addr': dict(pins=(0, 0)),
        'flaga': dict(pins=(0,)),
        'flagb': dict(pins=(0,)),
        'flagc': dict(pins=(0,)),
        'flagd': dict(pins=(0,)),
        
    }

    def get_flow(self, top=None):
        return ISE(brd=self, top=top)