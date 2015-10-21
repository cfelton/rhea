
from ..._fpga import _fpga
from ...toolflow import Vivado

class Zybo(_fpga):
    vendor = 'xilinx'
    family = 'zynq'
    device = 'XC7Z010'
    package = 'CLG400'
    speed = -1
    _name = 'zybo'
    
    default_clocks = {
        'clock': dict(frequency=50e6, pins=('E17',)),
    }

    default_resets = {
        'reset': dict(active=0, async=True, pins=('G14',),
                      iostandard='LVCMOS25', drive=4),
    }
    
    default_ports = {
        'led': dict(pins=('M14', 'M15', 'G14', 'D18',)),
        'btn': dict(pins=('R18', 'P16', 'V16', 'Y16')),
        'sw': dict(pins=('G15', 'P15', 'W13', 'T16',)),

        # audio
        'aubclk': dict(pins=('K18',)),
        'aupbdat': dict(pins=('M17',)),
        'aupblrc': dict(pins=('L17',)),
        'aurecdat': dict(pins=('L17',)),
        'aureclrc': dict(pins=('M18',)),
        'ausdin': dict(pins=('N17',)),
        'ausclk': dict(pins=('N18',)),
        'aumute': dict(pins=('P18',)),
        'aumclk': dict(pins=('T19',)),
    }

    def get_flow(self, top=None):
        return Vivado(brd=self, top=top)
        