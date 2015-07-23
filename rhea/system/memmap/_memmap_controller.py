
from __future__ import absolute_import
from __future__ import print_function

from copy import deepcopy
from myhdl import *
from ..regfile import Register


class MemMapController(object):
    def __init__(self, data_width=8, address_width=16):
        self.addr = Signal(intbv(0)[address_width:])
        self.wdata = Signal(intbv(0)[data_width:])
        self.rdata = Signal(intbv(0)[data_width:])
        self.read = Signal(bool(0))
        self.write = Signal(bool(0))
        self.done = Signal(bool(0))


def memmap_controller_basic(ctl, memap):
    """

    Ports:
    :param ctl:
    :param memap:
    :return:

    Parameters:

    """
    mm = memmap
