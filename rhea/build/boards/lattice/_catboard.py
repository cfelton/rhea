

from __future__ import absolute_import

from rhea.build import FPGA
from rhea.build.toolflow import IceRiver
from rhea.build.extintf import ExternalInterface
from rhea.build.extintf import Port 


class CATBoard(FPGA):
    vendor = 'lattice'
    family = 'ice40'
    device = 'HX8K'
    packet = 'CT256'
    _name = 'catboard'
    
    default_clocks = {
        'clock': dict(frequency=100e6, pins=('C8',))    
    }
    
    default_ports = {
        # the default port names match thoses in the schematic
        # but lower-case (and a couple exceptions)
        'led': dict(pins=('A9', 'B8', 'A7', 'B7',)),
        'sw': dict(pins=('A16', 'B9',)),
        'dipsw': dict(pins=('C6', 'C5', 'C4', 'C3',)),
        # the header index will not match the numbering on the
        # schematic because the nets in the schematic match
        # the header physical pins
        'hdr1': dict(pins=('J1', 'K1', 'H1', 'J2', 'H2', 'G2',
                           'G1', 'F2', 'F1', 'E2', 'F3', 'D1',
                           'E3', 'D2', 'C2', 'C1', 'B2', 'B1')),
        'bcm14_txd': dict(pins='T15'),
        'bcm15_rxd': dict(pins='T14'),
        
        'bcm9_miso': dict(pins='P12'),
        'bcm10_mosi': dict(pins='P11'),
        'bcm11_sclk': dict(pins='R11'),
        'bcm25': dict(pins='R12'),

        'bcm19_miso': dict(pins='T3'),
        'bcm20_mosi': dict(pins='R3'),
        'bcm21_sclk': dict(pins='T1'),
        'bcm16': dict(pins='R4'),
        'bcm26': dict(pins='T2'),
        'bcm3_scl': dict(pins='T16'),
        'bcm2_sda': dict(pins='R16'),
        
        # @todo: finish default ports
    }
    
    default_extintf = {
        # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        # SDRAM: the Xula2 has a 256Mbit WINBond SDRAM,        
        # @todo: merge into rhea.system/rhea.cores interfaces
        'sdram': ExternalInterface(
            Port('addr', pins=('F13', 'E14', 'E13', 'D14',   # 0-3
                               'B16', 'C16', 'D15', 'D16',   # 4-7
                               'E16', 'F15', 'F14', 'F16',   # 8-11
                               'G14',)                       # 12
            ),
            Port('data', pins=('R14', 'P14', 'M13', 'M14',   # 0-3
                               'L13', 'L14', 'K13', 'K14',   # 4-7
                               'J16', 'L16', 'M16', 'M15',   # 8-11
                               'N16', 'P16', 'P15', 'R15',)  # 12-15
            ),
            Port('bs',   pins=('H14', 'G13',)),
            Port('cas',  pins=('K15',)),
            Port('ras',  pins=('K16',)),
            Port('ldqm', pins=('J13',)),
            Port('udqm', pins=('J15',)),
            Port('clk',  pins=('H16',)),
            Port('clkfb', pins=('G16',)),
            Port('cs', pins=('H13',)),
            Port('we', pins=('J14',)),
            Port('cke',  pins=('G15',)),
            
            # timing information, all in ns
            timing = dict(
                init=200000.0,
                ras=45.0,
                rcd=20.0,
                ref=64000000.0,
                rfc=65.0,
                rp=20.0,
                xsr=75.0
             ),
            ddr=0  # single data rate
        ),
        
    }
    
    def get_flow(self, top=None):
        return IceRiver(brd=self, top=top)