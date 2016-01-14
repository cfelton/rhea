
from rhea.build import FPGA
from rhea.build.toolflow import ISE 


class UFO400(FPGA):
    vendor = 'xilinx'
    family = 'spartan3'
    device = 'XC3S400'
    package = 'tq144'
    speed = -4
    _name = 'ufo400'
    
    default_clocks = {
        'clock': dict(frequency=48e6, pins=(124,)),
    }
    
    default_resets = {
        'reset': dict(active=0, async=True, pins=(8,)),    
    }
    
    default_ports = {
        'led': dict(pins=(92, 93, 95, 96, 97, 98, 99, 100)),
                         
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