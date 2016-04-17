#
# Copyright (c) 2014-2015 Christopher Felton
#

from rhea.build import FPGA
from rhea.build.extintf import Port
# @todo: get SDRAM interface from rhea.cores.sdram
# from ...extintf._sdram import SDRAM
from rhea.build.toolflow import ISE


class Xula(FPGA):
    vendor = 'xilinx'
    family = 'spartan3A'
    device = 'XC3S200A'
    package = 'VQ100'
    speed = '-4'
    _name = 'xula'

    default_clocks = {
        'clock': dict(frequency=12e6, pins=(43,)),
        'chan_clk': dict(frequency=1e6, pins=(44,))
    }

    default_ports = {
        'chan': dict(pins=(36, 37, 39, 50, 52, 56, 57, 61,  # 0-7
                            62, 68, 72, 73, 82, 83, 84, 35,  # 8-15
                            34, 33, 32, 21, 20, 19, 13, 12,  # 17-23
                            7, 4, 3, 97, 94, 93, 89, 88))    # 24-31
    }

    def get_flow(self, top=None):
        return ISE(brd=self, top=top)


class XulaStickItMB(Xula):
    def __init__(self):
        """ StickIt board port definitions
        This class defines the port to pin mapping for the Xess StickIt
        board.  The Xula module can be plugged into the StickIt board.
        The StickIt board provides connections to many common physical
        interfaces: pmod, shields, etc.  Many of the pins are redefined
        to match the names of the connector connections
        """
        chan_pins = self.default_ports['chan']['pins']
        chan_pins = chan_pins + self.default_clocks['chan_clk']['pins']
        assert len(chan_pins) == 33
        self.default_ports['chan']['pins'] = chan_pins

        # the following are the bit-selects (chan[idx]) and not 
        # the pins.
        self.add_port_name('pm1', 'chan', (15, 32, 16, 0,   # pmod A
                                           11, 28, 13, 14)) # pmod B

        self.add_port_name('pm2', 'chan', (17, 1,  18, 3,   # pmod A
                                           15, 32, 16, 0))  # pmod B

        self.add_port_name('pm3', 'chan', (20, 4,  21, 5,   # pmod A
                                           17, 1,  18, 3))  # pmod B

        self.add_port_name('pm4', 'chan', (22, 6,  23, 7,   # pmod A
                                           20, 4,  21, 5))  # pmod B

        self.add_port_name('pm5', 'chan', (8,  25, 26, 10,  # pmod A
                                           22, 6,  23, 7))  # pmod B

        self.add_port_name('pm6', 'chan', (11, 28, 13, 14,  # pmod A
                                           8,  25, 26, 10)) # pmod B

        # @todo: add the wing defintions        


class Xula2(FPGA):
    vendor = 'xilinx'
    family = 'spartan6'
    device = 'XC6SLX25'
    package = 'FTG256'
    speed = '-2'
    _name = 'xula2'

    default_clocks = {
        'clock': dict(frequency=12e6, pins=('A9',)),
        'chan_clk': dict(frequency=1e6, pins=('T7',))
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


class Xula2StickItMB(Xula2):
    def __init__(self):
        """ """
        # to simplify the connector mapping append chan_clk to the
        # end of the channel pins.  Note overlapping ports cannot
        # be simultaneously used.
        chan_pins = self.default_ports['chan']['pins']
        chan_pins = chan_pins + self.default_clocks['chan_clk']['pins']
        # assert len(chan_pins) == 33, "len == {}".format(len(chan_pins))
        self.default_ports['chan']['pins'] = chan_pins

        super(Xula2StickItMB, self).__init__()

        self.add_port_name('pm1', 'chan', (0,  2,  4,  5,
                                           32, 1,  3,  5))

        self.add_port_name('pm2', 'chan', (15, 17, 19, 21,
                                           16, 18, 20, 22))

        self.add_port_name('pm3', 'chan', (23, 25, 27, 29,
                                           24, 26, 28, 30))
                   
        # @todo: add grove board connectors
        
        # RPi GPIO connector, each port defined as the 
        self.add_port_name('bcm2_sda', 'chan', 31)
        self.add_port_name('bcm3_scl', 'chan', 30)
        self.add_port_name('bcm4_gpclk0', 'chan', 29)
        self.add_port_name('bcm17', 'chan', 28)
        self.add_port_name('bcm27_pcm_d', 'chan', 27)
        self.add_port_name('bcm22', 'chan', 26)
        # ...
        self.add_port_name('bcm14_txd', 'chan', 14)
        self.add_port_name('bcm15_rxd', 'chan', 13)
        # @todo: finish ...
                    


                           