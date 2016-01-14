#
# Copyright (c) 2015 Christopher Felton, Nick Shaffner
#

from rhea.build import FPGA
from rhea.build.extintf import Port
from rhea.build.toolflow import ISE

class Anvyl(FPGA):
    vendor = 'xilinx'
    family = 'spartan6'
    device = 'XC6SLX45'
    package = 'CSG484'
    speed = '-3'
    _name = 'anvyl'

    default_clocks = {
        # 'clk' in documentation
        'clock': dict(frequency=100e6, pins=('D11',),
                    iostandard='LVCMOS33')        
    }
    
    default_ports = {
        # on-board switches
        'sw': dict(pins=('V5', 'U4', 'V3', 'P4',
                         'R4', 'P6', 'P5', 'P8',),
                   iostandard='LVCMOS18'),
        # on-board leds
        'led': dict(pins=('W3', 'Y4', 'Y1', 'Y3',
                          'AB4', 'W1', 'AB3', 'AA4'),
                    iostandard='LVCMOS18'),
        # on-board push-buttons
        'btn': dict(pins=('E6', 'D5', 'A3', 'AB9'),
                    iostandard='LVCMOS33')
    }

    def get_flow(self, top=None):
        return ISE(brd=self, top=top)
                    
                         
