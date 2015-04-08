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


class WishboneController(object):
    def __init__(self, data_width=8, address_width=16):
        self.addr = Signal(intbv(0)[address_width:])
        self.wdata = Signal(intbv(0)[data_width:])
        self.rdata = Signal(intbv(0)[data_width:])
        self.read = Signal(bool(0))
        self.write = Signal(bool(0))
        self.done = Signal(bool(0))


class Wishbone(MemMap):
    name = 'wishbone'
    
    def __init__(self, glbl=None, data_width=8, address_width=16, 
                 name=None):
        """
        Parameters (kwargs):
        --------------------
          glbl: system clock and reset
          data_width: data bus width
          address_width: address bus width
          name: name for the bus
        """
        # @todo: ?? not sure if this how the arguments should
        #        should be handled.  Passing args is simple but a
        #        little obscure ??
        super(Wishbone, self).__init__(data_width=data_width,
                                       address_width=address_width) 

        # note on Wishbone signal names, since the signals
        # are not passed to the controller and peripherals
        # (the interface is passed) there isn't a need for 
        # _o and _i on many of the signals.  Preserved the
        # peripheral (slave) point of view names.
        if glbl is None:
            self.clk_i = Clock(0)
        else:
            self.clk_i = glbl.clock

        if glbl.reset is None:
            self.rst_i = Reset(0, active=1, async=False)
        else:
            self.rst_i = glbl.reset
        
        self.cyc_i = Signal(bool(0))
        self.stb_i = Signal(bool(0))
        self.adr_i = Signal(intbv(0)[address_width:])
        self.we_i = Signal(bool(0))
        self.sel_i = Signal(bool(0))
        self.dat_i = Signal(intbv(0)[data_width:])

        # outputs from the peripherals
        self.dat_o = Signal(intbv(0)[data_width:])
        self.ack_o = Signal(bool(0))

        # peripheral outputs
        self._pdat_o = []
        self._pack_o = []

        self.clock = self.clk_i
        self.reset = self.rst_i        

        self.TIMEOUT = 1111

        # accessors (transactors) are generators, they don't return
        # only yield.  Need a mechanism to return data
        self.wval = 0
        self.rval = 0

        self._add_bus(name)
        
    def add_output_bus(self, name, dat, ack):
        self._pdat_o.append(dat)
        self._pack_o.append(ack)

    def m_per_outputs(self):
        """ combine all the peripheral outputs
        """
        assert len(self._pdat_o) == len(self._pack_o)
        ndevs = len(self._pdat_o)
        wb = self
        
        @always_seq(self.clk_i.posedge, reset=self.rst_i)
        def rtl_or_combine():
            dats = 0
            acks = 0
            for ii in range(ndevs):
                dats = dats | wb._pdat_o[ii]
                acks = acks | wb._pack_o[ii]
            wb.dat_o.next = dats
            wb.ack_o.next = acks
            
        return rtl_or_combine

    def m_per_interface(self, glbl, regfile, name='', base_address=0x00):
        """ memory-mapped wishbone peripheral interface
        """

        # local alias
        wb = self    # register bus
        rf = regfile # register file definition

        al,rl,rol,dl = rf.get_reglist()
        addr_list,regs_list = al,rl
        pwr,prd = rf.get_strobelist()
        nregs = len(regs_list)
        max_address = base_address + max(addr_list)

        # @todo: VHDL conversion can't handle a leading "_"
        lwb_do = Signal(intbv(0)[self.data_width:])
        (lwb_sel,lwb_acc,lwb_wr,
         lwb_wrd,lwb_ack,) = [Signal(bool(0)) for ii in range(5)]
        wb.add_output_bus(name, lwb_do, lwb_ack)
        
        ACNT = 1
        ackcnt = Signal(intbv(ACNT,min=0,max=ACNT+1))
        newcyc = Signal(bool(0))
        
        @always_comb
        def rtl_assign():
            lwb_acc.next = wb.cyc_i and wb.stb_i
            lwb_wr.next = wb.cyc_i and wb.stb_i and wb.we_i
                
        @always_seq(wb.clk_i.posedge, reset=wb.rst_i)
        def rtl_selected():
            if wb.cyc_i:
                if ackcnt > 0:
                    ackcnt.next = ackcnt - 1
                    if ackcnt == 1:
                        newcyc.next = True
            else:
                ackcnt.next = ACNT

            if wb.cyc_i and wb.adr_i >= base_address and wb.adr_i <= max_address:
                lwb_sel.next = True
            else:
                lwb_sel.next = False

            if wb.cyc_i and newcyc:
                lwb_ack.next = True
                newcyc.next = False
            else:
                lwb_ack.next = False

        # @todo: scan the register list, if it is contiguous remove
        #        the base and use the offset directly to access the
        #        the register list instead of the for loop
        # if rf.contiguous:
        #     @always_seq(rb.clk_i.posedge, reset=rb.rst_i)
        #     def rtl_read():
        # else:
        @always(wb.clk_i.posedge)
        def rtl_read():
            if wb.rst_i == int(wb.rst_i.active):
                for ii in range(nregs):
                    prd[ii].next = False
            else:
                if lwb_sel and not lwb_wr:                    
                    for ii in range(nregs):
                        aa = addr_list[ii]
                        aa = aa + base_address
                        if wb.adr_i == aa:
                            lwb_do.next = regs_list[ii]
                            prd[ii].next = True
                else:
                    lwb_do.next = 0
                    for ii in range(nregs):
                        prd[ii].next = False
                        
        @always(wb.clk_i.posedge)
        def rtl_write():
            if wb.rst_i == int(wb.rst_i.active):
                for ii in range(nregs):
                    ro = rol[ii]
                    dd = dl[ii]
                    if not ro:
                        regs_list[ii].next = dd
                    pwr[ii].next = False
            else:
                if lwb_wr and lwb_sel and not lwb_ack:                
                    for ii in range(nregs):
                        aa = addr_list[ii]
                        aa = aa + base_address
                        ro = rol[ii]
                        if not ro and wb.adr_i == aa:
                            regs_list[ii].next = wb.dat_i
                            pwr[ii].next = True
                else:
                    for ii in range(nregs):
                        pwr[ii].next = False

        # get the generators that assign the named bits
        gas = regfile.get_assigns()

        return instances()

    def get_controller_intf(self):
        return WishboneController(self.data_width, self.address_width)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def m_controller_basic(self, ctl):
        """
        Bus controllers (masters) are typically custom and 
        built into whatever the controller is (e.g a processor).
        This is a simple example with a simple interface to 
        invoke bus cycles.
        """
        wb = self
        States = enum('Idle', 'Write', 'WriteAck', 'Read', 'ReadAck', 'Done')
        state = Signal(States.Idle)
        TOMAX = 33
        tocnt = Signal(intbv(0, min=0, max=TOMAX))

        @always(wb.clock.posedge)
        def assign():
            wb.adr_i.next = ctl.addr
            wb.dat_i.next = ctl.wdata
            ctl.rdata.next = wb.dat_o


        @always_seq(wb.clock.posedge, reset=wb.reset)
        def rtl():
            # ~~~[Idle]~~~ 
            if state == States.Idle:
                if ctl.write:
                    state.next = States.Write
                    ctl.done.next = False
                elif ctl.read:
                    state.next = States.Read
                    ctl.done.next = False
                else:
                    ctl.done.next = True
                    
            # ~~~[Write]~~~
            elif state == States.Write:
                if not wb.ack_o:
                    wb.we_i.next = True
                    wb.cyc_i.next = True
                    wb.stb_i.next = True
                    state.next = States.WriteAck
                    tocnt.next = 0

            # ~~~[WriteAck]~~~
            elif state == States.WriteAck:
                if wb.ack_o:
                    wb.we_i.next = False
                    wb.cyc_i.next = False
                    wb.stb_i.next = False
                    state.next = States.Done

            # ~~~[Done]~~~
            elif state == States.Done:
                ctl.done.next = True
                if not (ctl.write or ctl.read):
                    state.next = States.Idle

            else:
                assert False, "Invalid state %s" % (state,)

        return assign, rtl

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    def write(self, addr, val):
        """ write accessor for testbenches
        """
        self.wval = val

        yield self.clk_i.posedge
        self.adr_i.next = addr
        self.dat_i.next = self.wval
        self.we_i.next = True
        self.cyc_i.next = True
        self.stb_i.next = True
        to = 0
        # wait for ack
        while not self.ack_o and to < self.TIMEOUT:
            yield delay(1) #self.clk_i.posedge
            to += 1
        self.we_i.next = False
        self.cyc_i.next = False
        self.stb_i.next = False
        yield self.clk_i.posedge

    def read(self, addr):
        """ read accessor for testbenches
        """
        yield self.clk_i.posedge
        self.adr_i.next = addr
        self.cyc_i.next = True
        self.stb_i.next = True
        to = 0
        while not self.ack_o and to < self.TIMEOUT:
            yield self.clk_i.posedge
            to += 1
        self.cyc_i.next = False
        self.stb_i.next = False
        self.rval = self.dat_o

    @property
    def readval(self):
        return self.rval
