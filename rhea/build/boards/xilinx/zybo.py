
from rhea.build import FPGA
from rhea.build.toolflow import Vivado


class Zybo(FPGA):
    vendor = 'xilinx'
    family = 'zynq'
    device = 'XC7Z010'
    package = 'CLG400'
    speed = -1
    _name = 'zybo'
    
    default_clocks = {
        'clock': dict(frequency=125e6, pins=('L16',),
                      iostandard='LVCMOS33'),
    }

    # default_resets = {
    #     'reset': dict(active=0, async=True, pins=('G14',),
    #                   iostandard='LVCMOS25'),  #  drive=4
    # }
    
    default_ports = {
        'led': dict(pins=('M14', 'M15', 'G14', 'D18',),
                    iostandard='LVCMOS33'),
        'btn': dict(pins=('R18', 'P16', 'V16', 'Y16'),
                    iostandard='LVCMOS33'),
        'sw': dict(pins=('G15', 'P15', 'W13', 'T16',),
                   iostandard='LVCMOS33'),

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

        # PMODs
        'pmod_jb': dict(pins=('T20', 'U20', 'V20', 'W20',
                              'Y18', 'Y19', 'W18', 'W19',),
                        iostandard="LVDS_25"),

        # je is the 'standard' pmod
        'pmod_je': dict(pins=('V12', 'W16', 'J15', 'H15',
                              'V13', 'U17', 'T17', 'Y17',),
                        iostandard='LVCMOS33'),

        # VGA (names from the reference manual but lowercase and
        # with the "vga_" prefix)
        'vga_red': dict(pins=('M19', 'L20', 'J20', 'G20', 'F19',),
                        iostandard='LVCMOS33'),
        'vga_grn': dict(pins=('H18', 'N20', 'L19', 'J19', 'H20', 'F20',),
                        iostandard='LVCMOS33'),
        'vga_blu': dict(pins=('P20', 'M20', 'K19', 'J18', 'G19'),
                        iostandard='LVCMOS33'),
        'vga_hsync': dict(pins=('P19',), iostandard='LVCMOS33'),
        'vga_vsync': dict(pins=('R19',), iostandard='LVCMOS33'),
    }

    def get_flow(self, top=None):
        return Vivado(brd=self, top=top)
