#
# Copyright (c) 2015 Christopher Felton
#

from __future__ import absolute_import

from ..._fpga import _fpga
from ...extintf import Port
from ...toolflow import IceRiver


class Icestick(_fpga):
    vendor = 'lattice'
    family = 'ice'
    device = 'ice40'
    package = ''
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
    }

    def get_flow(self, top=None):
        return IceRiver(brd=self, top=top)

