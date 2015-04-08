#
# Copyright (c) 2014-2015 Christopher L. Felton
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

from __future__ import absolute_import

from myhdl import *
from mn.system import Clock
from mn.system import Reset
from mn.system.memmap._memmap import MemMap


class AvalonMM(MemMap):
    name = 'avalon'

    def __init__(self, glbl=None, data_width=8, address_width=16,
                 name=None):
        """
        Parameters (kwargs):
        --------------------
        :param glbl: system clock and reset
        :param data_width: data bus width
        :param address_width: address bus width
        :param name: name for the bus
        """
        super(AvalonMM, self).__init__(data_width=data_width,
                                       address_width=address_width)
        if glbl is None:
            self.clk = Clock(0)
        else:
            self.clk = glbl.clock

        if glbl.reset is None:
            self.reset = Reset(0, active=1, async=False)
        else:
            self.reset = glbl.reset

        self.address = Signal(intbv(0)[address_width:])
        self.byteenable = Signal(intbv(0)[2:])
        self.read = Signal(bool(0))
        self.write = Signal(bool(0))
        self.waitrequest = Signal(bool(0))
        self.readdatavalid = Signal(bool(0))
        self.readdata = Signal(intbv(0)[data_width:])
        self.writedata = Signal(intbv(0)[data_width:])
        self.response = Signal(intbv(0)[2:])


    def add_output_bus(self, name, readdata, readdatavalid, waitrequest):
        self._readdata.append(readdata)
        self._readatavalid.append(readdatavalid)
        self._waitrequest.append(waitrequest)


    def m_per_outputs(self):
        """ combine all the peripheral outputs
        """
        assert len(self._readata) == len(self._readatavalid)
        ndevs = len(self._readdata)

        av = self

        @always_seq(self.clk.posedge, reset=self.reset)
        def rtl_or_combine():
            rddats = 0
            valids = 0
            for ii in range(ndevs):
                rddats = rddats | av._readdata[ii]
                valids = valids | av._readdatavalid[ii]
            av.readdata.next = rddats
            av.readdatavalid.next = valids

        return rtl_or_combine


    def m_per_interface(self, glbl, regfile, name='', base_address=0x0):
        """ memory-mapped avalon peripheral interface
        """

        # local alias
        av = self      # register bus
        rf = regfile   # register file definition

