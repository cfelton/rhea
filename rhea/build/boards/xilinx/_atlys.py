

from rhea.build import FPGA
from rhea.build.toolflow import ISE 


class Atlys(FPGA):
    vendor = 'xilinx'
    family = 'spartan6'
    device = 'XC6SLX45'
    package = 'CSG324'
    speed = -3
    _name = 'atlys'
    
    default_clocks = {
        'clock': dict(frequency=50e6, pins=('L15',)),
    }

    default_resets = {
        'reset': dict(active=0, async=True, pins=('T15',)),
    }
    
    default_ports = {
        'led': dict(pins=('U18', 'M14', 'N14', 'L14', 
                          'M13', 'D4', 'P16', 'N12',)),

        'btn': dict(pins=('N4', 'P4', 'P3', 'F6', 'F5',)),
        'sw': dict(pins=('A10', 'D14', 'C14', 'P15',
                         'P12', 'R5', 'T5', 'E4',)),
        
        # the port names are from the FPGA perspective, swapped
        # from the net names used in the digilent reference manual
        'uart_rx': dict(pins=('A16',)),  # external transmit / internal rx
        'uart_tx': dict(pins=('B16',)),  # external receive / internal tx
        
        'pmod': dict(pins=('T3', 'R3', 'P6', 'N5',
                           'V9', 'T9', 'V4', 'T4')),

        # VHDCI expansion connector (diff pairs)
        'iop': dict(pins=('U16', 'U15', 'U13', 'M11',)),
        'ion': dict(pins=('V16', 'V15', 'V13', 'N11',))
    }

    def get_flow(self, top=None):
        return ISE(brd=self, top=top)