

from __future__ import absolute_import

from ..._fpga import _fpga
from ...toolflow import IceRiver


class CATBoard(_fpga):
    vendor = 'lattice'
    family = 'ice40'
    device = 'HX8K'
    packet = 'CT256'
    _name = 'catboard'
    
    default_clocks = {
        'clock': dict(freqeuncy=100e6, pins=('C8',))    
    }
    
    default_ports = {
        'led': dict(pins=('A9', 'B8', 'A7', 'B7',)),
        'sw': dict(pins=('A16', 'B9',)),
        'dipsw': dict(pins=('C6', 'C5', 'C4', 'C3',)),
        'hdr1': dict(pins=('J1', 'K1', 'H1', 'J2', )),
        # @todo: finish default ports

    }
    
    def get_flow(self, top=None):
        return IceRiver(brd=self, top=top)