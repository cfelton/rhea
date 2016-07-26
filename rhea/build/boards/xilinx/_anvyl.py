#
# Copyright (c) 2015 Christopher Felton, Nick Shaffner
#
# Anvyl Master UCFReference:
#   https://digilentinc.com/Data/Products/ANVYL/ANVYL-Master_UCF.zip
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
        'clock': dict(frequency=100e6, pins=('D11',), iostandard='LVCMOS33')
    }
    
    default_ports = {
        # on-board leds
        'led': dict(pins=('W3', 'Y4', 'Y1', 'Y3', 'AB4', 'W1', 'AB3', 'AA4',),
                    iostandard='LVCMOS18'),

        # 2x gyr leds
        'ldt1g': dict(pins=('T7',), iostandard='LVCMOS18'),
        'ldt1y': dict(pins=('W4',), iostandard='LVCMOS18'),
        'ldt1r': dict(pins=('U8',), iostandard='LVCMOS18'),
        'ldt2g': dict(pins=('R7',), iostandard='LVCMOS18'),
        'ldt2y': dict(pins=('U6',), iostandard='LVCMOS18'),
        'ldt2r': dict(pins=('T8',), iostandard='LVCMOS18'),

        # on-board switches
        'sw': dict(pins=('V5', 'U4', 'V3', 'P4', 'R4', 'P6', 'P5', 'P8',),
                   iostandard='LVCMOS18'),

        # on-board push-buttons
        'btn': dict(pins=('E6', 'D5', 'A3', 'AB9',),
                    iostandard='LVCMOS33'),

        # keypad
        'kypd_col': dict(pins=('H8', 'J7', 'K8', 'K7',),
                    iostandard='LVCMOS18'),
        'kypd_row': dict(pins=('E4', 'F3', 'G8', 'G7',),
                    iostandard='LVCMOS18'),

        # breadboard
        'bb': dict(pins=('AB20', 'P17', 'P18', 'Y19', 'Y20', 'R15', 'R16', 'R17', 'R19', 'V19',),
                   iostandard='LVCMOS33'),

        # dip banks a & b
        'dipa': dict(pins=('G6','G4','F5','E5',), iostandard='LVCMOS18'),
        'dipb': dict(pins=('F8','F7','C4','D3',), iostandard='LVCMOS18'),

        # rs232
        'rs232_uart_tx': dict(pins=('T19',), iostandard='LVCMOS33'),
        'rs232_uart_rx': dict(pins=('T20',), iostandard='LVCMOS33'),

        # iic
        'iic_sda': dict(pins=('C5',), pullup=True, iostandard='LVCMOS33'),
        'iic_scl': dict(pins=('A4',), pullup=True, iostandard='LVCMOS33'),




        # sram
        #sram_address
        #sram_data
        #...

    }

    def get_flow(self, top=None):
        return ISE(brd=self, top=top)
                    
                         
