#
# Copyright (c) 2006-2013 Christopher L. Felton
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

def fifo_mem_generic(
    wclk,         # write sync clock
    wr,           # Write strobe
    din,          # data in (write data)
    addr_w,       # write address

    rclk,         # read sync clock
    dout,         # data out (write data)
    addr_r,       # read address
    
    DSZ = 8,      # Data Size
    ASZ = 9       # Address Size
    ):
    """
    Timing Diagram:
    """
    mem = [Signal(intbv(0)[DSZ:]) for ii in range(2**ASZ)]
    #_addr_r = Signal(intbv(0)[ASZ:])
    _addr_w = Signal(intbv(0)[ASZ:])
    _din    = Signal(intbv(0)[DSZ:])
    _dout   = Signal(intbv(0)[DSZ:])
    _wr     = Signal(False)

    @always_comb
    def dout_rtl():
        dout.next = _dout
        
    @always(rclk.posedge)
    def rd_rtl():
        _dout.next = mem[int(addr_r)]        
        
    @always(wclk.posedge)
    def wr_rtl():
        _wr.next     = wr
        _addr_w.next = addr_w
        _din.next    = din

    @always(wclk.posedge)
    def rtl_mem():
        if _wr:
            mem[int(_addr_w)].next = _din

    # Debug Only
    m0  = Signal(intbv(0)[8:])
    m1  = Signal(intbv(0)[8:])
    m2  = Signal(intbv(0)[8:])
    m3  = Signal(intbv(0)[8:])
    m4  = Signal(intbv(0)[8:])
    m5  = Signal(intbv(0)[8:])
    m6  = Signal(intbv(0)[8:])
    m7  = Signal(intbv(0)[8:])
    m8  = Signal(intbv(0)[8:])
    m9  = Signal(intbv(0)[8:])
    m10 = Signal(intbv(0)[8:])
    m11 = Signal(intbv(0)[8:])
    m12 = Signal(intbv(0)[8:])
    m13 = Signal(intbv(0)[8:])
    m14 = Signal(intbv(0)[8:])
    m15 = Signal(intbv(0)[8:])
    
    @always_comb
    def sim_debug():
        m0.next = mem[0]
        m1.next = mem[1]
        m2.next = mem[2]
        m3.next = mem[3]
        m4.next = mem[4]
        m5.next = mem[5]
        m6.next = mem[6]
        m7.next = mem[7]
        m8.next = mem[8]
        m9.next = mem[9]
        m10.next = mem[10]
        m11.next = mem[11]
        m12.next = mem[12]
        m13.next = mem[13]
        m14.next = mem[14]
        m15.next = mem[15]

    return instances()


# @todo if needed create fifo memory for different devices
# To directly instantiate a device specific memory use the
#  __verilog__ or __vhdl__ here instead.
# @todo example
#
# def fifo_mem_XS3
# def fifo_mem_XS3E
# def fifo_mem_CYC3
# ....

def convert():
    DSZ = 8
    ASZ = 9

    clk     = Signal(False)
    wr      = Signal(False)
    din     = Signal(intbv(0)[DSZ:])
    dout    = Signal(intbv(0)[DSZ:])
    addr_w  = Signal(intbv(0)[ASZ:])
    addr_r  = Signal(intbv(0)[ASZ:])

    toVerilog(fifo_mem_generic, clk, wr, din, dout, addr_w, addr_r)
    toVHDL(fifo_mem_generic, clk, wr, din, dout, addr_w, addr_r)

if __name__ == '__main__':
    convert()


