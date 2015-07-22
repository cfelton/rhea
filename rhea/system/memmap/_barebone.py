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

from ._memmap import MemMap

class Barebone(MemMap):
    def __init__(self, data_width=8, address_width=16):
        self.wr = Signal(False)
        self.rd = Signal(False)
        self.ack = Signal(False)
        self.rdat = Signal(intbv(0)[data_width:])
        self.wdat = Signal(intbv(0)[data_width:])
        self.addr = Signal(intbv(0)[address_width:])
        super(Barebone, self).__init__(data_width=data_width,
                                       address_width=address_width) 

        