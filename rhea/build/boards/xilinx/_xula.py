#
# Copyright (c) 2014-2015 Christopher Felton
#

from ..._fpga import _fpga
from ...extintf import Port
# @todo: get SDRAM interface from rhea.cores.sdram
# from ...extintf._sdram import SDRAM
from ...toolflow import ISE


class Xula(_fpga):
    vendor = 'xilinx'
    family = 'spartan3A'
    device = 'XC3S200A'
    package = 'VQ100'
    speed = '-4'
    _name = 'xula'

    default_clocks = {
        'clock': dict(frequency=12e6, pins=(43,)),
        'chan_clk' : dict(frequency=1e6, pins=(44,))
    }

    default_ports = {
        'chan' : dict(pins=(36, 37, 39, 50, 52, 56, 57, 61,  # 0-7
                            62, 68, 72, 73, 82, 83, 84, 35,  # 8-15
                            34, 33, 32, 21, 20, 19, 13, 12,  # 17-23
                            7, 4, 3, 97, 94, 93, 89, 88))    # 24-31
    }

    def get_flow(self, top=None):
        return ISE(brd=self, top=top)


class Xula2(_fpga):
    vendor = 'xilinx'
    family = 'spartan6'
    device = 'XC6SLX25'
    package = 'FTG256'
    speed = '-2'
    _name = 'xula2'

    default_clocks = {
        'clock': dict(frequency=12e6, pins=('A9',)),
        'chan_clk': dict(frequency=1e6, pins=('T7'))
    }

    default_ports = {
        'chan': dict(pins=('R7','R15','R16','M15','M16','K15',  #0-5
                           'K16','J16','J14','F15','F16','C16', #6-11
                           'C15','B16','B15','T4','R2','R1',    #12-17
                           'M2','M1','K3','J4','H1','H2',       #18-23
                           'F1','F2','E1','E2','C1','B1',       #24-29
                           'B2','A2',) )
    }


    default_extintf = {
        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # VGA:
        'vga': None,  

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # SDRAM: the Xula2 has a 256Mbit WINBond SDRAM,        
        # http://www.winbond.com/hq/enu/ProductAndSales/ProductLines/SpecialtyDRAM/SDRAM/W9825G6JH.htm
        # @todo: mege into rhea.syste/rhea.cores intefaces
        # 'sdram': SDRAM(
        #     Port('addr', pins=('E4',  'E3',  'D3',  'C3',   # 0-3
        #                        'B12', 'A12', 'D12', 'E12',  # 4-7
        #                        'G16', 'G12', 'F4',  'G11',  # 8-11
        #                        'H13',)                      # 12
        #          ),
        #     Port('data', pins=('P6',  'T6',  'T5',  'P5',   # 0-3
        #                        'R5',  'N5',  'P4',  'N4',   # 4-7
        #                        'P12', 'R12', 'T13', 'T14',  # 8-11
        #                        'R14', 'T15', 'T12', 'P11',) # 12-15
        #      ),
        #     Port('bs',   pins=('H3', 'G3',) ),
        #     Port('cas',  pins=('L3',) ),
        #     Port('ras',  pins=('L4',) ),
        #     Port('ldqm', pins=('M4',) ),
        #     Port('udqm', pins=('L13',) ),
        #     Port('clk',  pins=('K12',) ),
        #     Port('clkfb', pins=('K11',) ),
        #     Port('cs', pins=('H4',) ),
        #     Port('we', pins=('M3',) ),
        #     Port('cke',  pins=('J12',)),
        #     
        #     # timing information, all in ns
        #     timing = dict(
        #         init = 200000.0,
        #         ras  = 45.0,
        #         rcd  = 20.0,
        #         ref  = 64000000.0,
        #         rfc  = 65.0,
        #         rp   = 20.0,
        #         xsr  = 75.0                  
        #      ),
        #     ddr = 0  # single data rate
        # ),

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        #  SPI and MicroSD
        #'flash': _extintf(
        #    Port('sclk', pins=()),
        #    Port('sdi', pins=()),
        #    Port('sdo', pins=()),
        #    port('cs', pins=()),
        #    ),
        #
        #'microsd' : None,

        #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # 
    }


    def get_flow(self, top=None):
        return ISE(brd=self, top=top)
