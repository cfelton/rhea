#
# Copyright (c) 2006-2014 Christopher L. Felton
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


from myhdl import *

def m_sync_rst(clock, rsti, rsto):
    """
    """
    rsync = [Signal(bool(rsti.active)) for _ in range(2)]


    @always_seq(clock.posedge, reset=rsti)
    def rtl():        
        rsync[0].next = rsti
        rsync[1].next = rsync[0]
        rsto.next = rsync[1]

    return rtl

def m_sync_mbits(clock, reset, sigin, sigou):

    d1 = Signal(intbv(0)[len(sigou):])

    @always_seq(clock.posedge, reset=reset)
    def rtl():
        d1.next = sigin
        sigou.next = d1

    return rtl