#
# Copyright (c) 2013-2015 Christopher L. Felton
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from argparse import Namespace

from myhdl import *

from ...cores.fifo._fifo_async import fifo_async

_fb_num = 0
_fb_list = {}


def _add_bus(fb, name=''):
    """ globally keep track of all the busses added.
    """
    global _fb_num, _fb_list
    _fb_num += 1
    _fb_list[name] = fb


class FIFOBus(object):
    """
    """
    def __init__(self, size=16, width=8):
        self.name = "fifobus{0}".format(_fb_num)
        
        # all the data signals are from the perspective
        # of the FIFO being interfaced to.        
        self.clear = Signal(bool(0))           # fifo clear
        #self.wclk = None                      # write side clock
        self.wr = Signal(bool(0))              # write strobe to fifo
        self.wdata = Signal(intbv(0)[width:])  # fifo data in

        #self.rclk = None                      # read side clock
        self.rd = Signal(bool(0))              # fifo read strobe
        self.rdata = Signal(intbv(0)[width:])  # fifo data out
        self.rvld = Signal(bool(0))
        self.empty = Signal(bool(1))           # fifo empty
        self.full = Signal(bool(0))            # fifo full
        self.count = Signal(intbv(0, min=0, max=size))

        self.width = width
        self.size = size

        _add_bus(self, self.name)


    # @todo: waffling if this should be included or not???
    #def m_fifo(self, reset, wclk, rclk):
    #    #self.wclk = wclk
    #    #self.rclk = rclk
    #    # map the FIFO interface to the actual fifo
    #    gfifo = fifo_async(reset, wclk, rclk, self)
    #    return gfifo

    # @todo: get the separate buses
    # def get_upstream()    
    #     """ write bus, into the FIFO """
    # def get_downstream()
    #     """ 