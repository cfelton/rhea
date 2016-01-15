#
# Copyright (c) 2015 Christopher Felton, Nick Shaffner
#

from myhdl import TristateSignal, intbv

from rhea.build import FPGA
from rhea.build.extintf import Port
from rhea.build.toolflow import ISE


class Mojo(FPGA):
    vendor = 'xilinx'
    family = 'spartan6'
    device = 'XC6SLX9'
    package = 'TQG144'
    speed = '-2'
    version = 3
    _name = 'mojov'
    no_startup_jtag_clock = True
    
    default_clocks = {
        # clk in documentation (?)
        'clock': dict(frequency=50e6, pins=(56,),
                    iostandard='LVTTL')        
    }

    default_resets = {
        # rst_n in documentation
        'reset': dict(active=0, async=True, pins=(38,),
                      iostandard='LVTTL')
    }
    
    default_ports = {
        # on-board led
        'led': dict(pins=(134, 133, 132, 131,
                          127, 126, 124, 123,),
                   iostandard='LVTTL'),
        'cclk': dict(pins=(70,), iostandard='LVTTL'),

        'spi_mosi': dict(pins=(44,), iostandard='LVTTL'),
        'spi_miso': dict(pins=(45,), iostandard='LVTTL'),
        'spi_ss': dict(pins=(48,), iostandard='LVTTL'),
        'spi_sck': dict(pins=(43,), iostandard='LVTTL'),
        'spi_channel': dict(pins=(46, 61, 62, 65,),
                            sigtype=TristateSignal(intbv(0)[4:]),
                            iostandard='LVTTL'),
        'avr_tx': dict(pins=(55,), iostandard='LVTTL'),
        'avr_rx': dict(pins=(59,), iostandard='LVTTL'),
        'avr_tx_busy': dict(pins=(39,), iostandard='LVTTL'),
    }

    def get_flow(self, top=None):
        return ISE(brd=self, top=top)
