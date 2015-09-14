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

    default_clocks = {}
    default_ports = {}

    def get_flow(self, top=None):
        return IceRiver(brd=self, top=top)

