
from ..._fpga import _fpga
from ...toolflow import Vivado

class Parallella(_fpga):
    vendor = 'xilinx'
    family = 'zynq'
    device = 'XC7Z010'
    package = 'CLG400'
    speed = -1
    _name = 'parallella'
    
    default_clocks = {
        # @todo: fix clock ...
        'clock': dict(frequency=50e6, pins=('E17',)),
        'elink_rxi_cclk_p': dict(pins=('',)),
        'elink_rxi_cclk_n': dict(pins=('',)),
        'elink_rxi_lclk_p': dict(pins=('',)),
        'elink_rxi_lclk_n': dict(pins=('',)),
        'elink_txo_lclk_p': dict(pins=('',)),
        'elink_txo_lclk_n': dict(pins=('',)),
    }

    default_resets = {
        'dsp_reset_n': dict(active=0, async=True, pins=('G14',),
                            iostandard='LVCMOS25', drive=4),
    }
    
    default_ports = {
        # the parallella doesn't have leds, for the tests
        # need an led port.  These will be ignored in actual
        # parallella designs
        'led': dict(pins=('M14', 'M15', 'G14', 'D18',)),
        
        'gpio_p': dict(pins=('T16', 'V16', 'P15', 'U18', 
                             'P14', 'T14', 'U14', 'W14',
                             'U13', 'V12', 'T12', 'T11')),

        'gpio_n': dict(pins=('U17', 'W16', 'P16', 'U19', 
                             'R14', 'T15', 'U15', 'Y14',
                             'V13', 'W13', 'U12', 'T10')),

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
        
        # hdmi
    }

    def get_flow(self, top=None):
        return Vivado(brd=self, top=top)
        