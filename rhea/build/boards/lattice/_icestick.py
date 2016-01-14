#
# Copyright (c) 2015 Christopher Felton
#

from __future__ import absolute_import

from rhea.build import FPGA
from rhea.build.extintf import Port
from rhea.build.toolflow import IceRiver


class Icestick(FPGA):
    vendor = 'lattice'
    family = 'ice40'
    device = 'HX1K'
    package = 'TQ144'
    _name = 'icestick'

    default_clocks = {
        'clock': dict(frequency=12e6, pins=(21,))
    }
    
    default_ports = {
        'led': dict(pins=(99, 98, 97, 96, 95,)),
        'spi_sck': dict(pins=(70,)),
        'spi_si': dict(pins=(68,)),
        'spi_so': dict(pins=(67,)),
        'spi_ss': dict(pins=(71,)),
        'uart_tx': dict(pins=(8,)),
        'uart_rx': dict(pins=(9,)),
        'uart_dtr': dict(pins=(3,)),
        'uart_rts': dict(pins=(7,)),
        'pmod': dict(pins=(78, 79, 80, 81, 87, 88, 90, 91,)),
    }

    def get_flow(self, top=None):
        return IceRiver(brd=self, top=top)

