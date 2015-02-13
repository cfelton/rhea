
# Copyright (c) 2014 Christopher L. Felton
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

from math import log, fmod, ceil
from myhdl import *

from _fifo_intf import check_fifo_intf
from _fifo_intf import _fifobus
from _fifo_mem import m_fifo_mem_generic

def m_fifo_sync(clock, reset, fbus):
    """ Simple synchronous FIFO

    PORTS
    =====

    PARAMETERS
    ==========
    """

    # @todo: this is intended to be used for small fast fifo's but it
    #        can be used for large synchronous fifo as well
    N = fbus.size

    if fmod(log(N, 2), 1) != 0:
        Asz = int(ceil(log(N,2)))
        N = 2**Asz
        print("@W: m_fifo_sync only supports power of 2 size")
        print("    forcing size (depth) to %d instread of " % (N, fbus.size)) 

    wptr = Signal(modbv(0, min=0, max=N))
    rptr = Signal(modbv(0, min=0, max=N))
    _vld     = Signal(False)

    # generic memory model
    g_fifomem = m_fifo_mem_generic(clock, fbus.wr, fbus.wdata, wptr,
                                   clock, fbus.rdata, rptr,
                                   mem_size=fbus.size)

    # @todo: almost full and almost empty flags
    read = fbus.rd
    write = fbus.wr
    @always_seq(clock.posedge, reset=reset)
    def rtl_fifo():
        if fbus.clear:
            wptr.next = 0
            rptr.next = 0
            fbus.full.next = False
            fbus.empty.next = True

        elif read and not write:
            fbus.full.next = False
            if not fbus.empty:
                rptr.next = rptr + 1
            if rptr == (wptr-1):
                fbus.empty.next = True

        elif write and not read:
            fbus.empty.next = False
            if not fbus.full:
                wptr.next = wptr + 1
            if wptr == (rptr-1):
                fbus.full.next = True

        elif write and read:
            wptr.next = wptr + 1
            rptr.next = rptr + 1

        _vld.next = read

    @always_comb
    def rtl_assign():
        fbus.rvld.next = _vld & fbus.rd
                
    nvacant = Signal(intbv(N, min=-0, max=N+1))  # # empty slots
    ntenant = Signal(intbv(0, min=-0, max=N+1))  # # filled slots
    
    @always_seq(clock.posedge, reset=reset)
    def dbg_occupancy():
        if fbus.clear:
            nvacant.next = N
            ntenant.next = 0
        else:
            v = nvacant
            f = ntenant
            
            if fbus.rvld:
                v = v + 1
                f = f - 1
            if fbus.wr:
                v = v -1 
                f = f + 1

            nvacant.next = v
            ntenant.next = f

    fbus.count = ntenant

    return (g_fifomem, rtl_fifo, rtl_assign, dbg_occupancy,)

# attached a generic fifo bus object to the module
m_fifo_sync.fbus_intf = _fifobus