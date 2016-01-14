
from rhea.build import FPGA
from rhea.build.toolflow import Vivado


class Parallella(FPGA):
    vendor = 'xilinx'
    family = 'zynq'
    device = 'XC7Z010'
    package = 'CLG400'
    speed = -1
    _name = 'parallella'
    
    default_clocks = {
        # @todo: fix clock ...
        'clock': dict(frequency=50e6, pins=('R16',),
                  iostandard='LVCMOS25', ),
        'elink_rxi_cclk_p': dict(pins=('',)),
        'elink_rxi_cclk_n': dict(pins=('',)),
        'elink_rxi_lclk_p': dict(pins=('',)),
        'elink_rxi_lclk_n': dict(pins=('',)),
        'elink_txo_lclk_p': dict(pins=('',)),
        'elink_txo_lclk_n': dict(pins=('',)),
    }

    default_resets = {}
    
    default_ports = {
        # this is an 8 LED PMOD on the porcupine board
        'led': dict(pins=('U18', 'P15', 'U19', 'P16',
                          'V16', 'T16', 'W16', 'U17',),
                iostandard='LVCMOS25'),

        # GPIO available on the porcupine board, 24 diff pair
        # first 12 on the 70x0 second 12 only on 7020
        'gpio_p': dict(pins=('T16', 'V16', 'P15', 'U18', 
                             'P14', 'T14', 'U14', 'W14',
                             'U13', 'V12', 'T12', 'T11', 
                             'Y12', 'W11', 'V11', 'T9',
                             'W10', 'U9',  'V8',  'Y9',
                             'Y7',  'U7',  'V6',  'T5',),
                   iostandard='LVDS_25'),

        'gpio_n': dict(pins=('U17', 'W16', 'P16', 'U19', 
                             'R14', 'T15', 'U15', 'Y14',
                             'V13', 'W13', 'U12', 'T10',
                             'Y13', 'Y11', 'V10', 'U10',
                             'W9',  'U8',  'W8',  'Y8',
                             'Y6',  'V7',  'W6',  'U5',),
                   iostandard='LVDS_25'),

        # elink
        'elink_rxi_data_p': dict(pins=('',)),
        'elink_rxi_data_n': dict(pins=('',)),
        'elink_rxi_frame_p': dict(pins=('',)),
        'elink_rxi_frame_n': dict(pins=('',)),
        'elink_rxo_rd_wait_p': dict(pins=('',)),
        'elink_rxo_rd_wait_n': dict(pins=('',)),
        'elink_rxo_wr_wait_p': dict(pins=('',)),
        'elink_rxo_wr_wait_n': dict(pins=('',)),
        
        'elink_txo_data_p': dict(pins=('',)),
        'elink_txo_data_n': dict(pins=('',)),
        'elink_txo_frame_p': dict(pins=('',)),
        'elink_txo_frame_n': dict(pins=('',)),
        'elink_txi_rd_wait_p': dict(pins=('',)),
        'elink_txi_rd_wait_n': dict(pins=('',)),
        'elink_txi_wr_wait_p': dict(pins=('',)),
        'elink_txi_wr_wait_n': dict(pins=('',)),

        'dsp_reset_n': dict(pins=('G14',), 
                            iostandard='LVCMOS25', drive=4),

        
        # hdmi

        # USB-UART
        
    }

    def get_flow(self, top=None):
        return Vivado(brd=self, top=top)
        