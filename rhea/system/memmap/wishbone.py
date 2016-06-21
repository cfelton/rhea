#
# Copyright (c) 2014-2015 Christopher L. Felton
#

from __future__ import absolute_import

import myhdl
from myhdl import (Signal, intbv, always, always_seq, always_comb,
                   instance, instances, concat, enum, now)

from ..glbl import Global
from . import MemoryMapped
from . import Barebone


class Wishbone(MemoryMapped):
    name = 'wishbone'

    def __init__(self, glbl=None, data_width=8, address_width=16, name=None):
        """ Wishbose bus object
        Parameters (kwargs):
        --------------------
          :param glbl: system clock and reset
          :param data_width: data bus width
          :param address_width: address bus width
          :param name: name for the bus
        """
        # @todo: ?? not sure if this how the arguments should
        #        should be handled.  Passing args is simple but a
        #        little obscure ??
        super(Wishbone, self).__init__(data_width=data_width,
                                       address_width=address_width) 

        # note on Wishbone signal names, since the signals
        # are not passed to the controller and peripherals
        # (the interface is passed) there isn't a need for 
        # _o and _i on many of the signals.  
        # Preserved the peripheral (slave) point of view names.
        if glbl is not None:
            self.clock = glbl.clock
        self.clk_i = self.clock

        if glbl is not None and glbl.reset is not None:
            self.reset = glbl.reset
        self.rst_i = self.reset
        
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

        self.timeout = 1111

        self._add_bus(name)
        
    def add_output_bus(self, dat, ack):
        self._pdat_o.append(dat)
        self._pack_o.append(ack)

    @myhdl.block
    def interconnect(self):
        """ combine all the peripheral outputs
        """
        assert len(self._pdat_o) == len(self._pack_o)
        ndevs = len(self._pdat_o)
        wb = self
        
        @always_seq(self.clk_i.posedge, reset=self.rst_i)
        def beh_or_combine():
            dats = 0
            acks = 0
            for ii in range(ndevs):
                dats = dats | wb._pdat_o[ii]
                acks = acks | wb._pack_o[ii]
            wb.dat_o.next = dats
            wb.ack_o.next = acks
            
        return beh_or_combine

    @myhdl.block
    def peripheral_regfile(self, regfile, name=''):
        """ memory-mapped wishbone peripheral interface
        """

        # local alias
        wb = self     # register bus
        rf = regfile  # register file definition
        clock, reset = wb.clk_i, wb.rst_i

        # @todo: base address default needs to be revisited
        # if the base_address is not set, simply set to 0 for now ...
        base_address = regfile.base_address 
        if base_address is None:
            base_address = 0 
        
        # get the address list (al), register list (rl), read-only list (rol),
        # and the default list (dl).
        al, rl, rol, dl = rf.get_reglist()
        addr_list, regs_list = al, rl
        pwr, prd = rf.get_strobelist()

        nregs = len(regs_list)
        max_address = base_address + max(addr_list)

        lwb_do = Signal(intbv(0)[self.data_width:])
        (lwb_sel, lwb_acc, lwb_wr,
         lwb_wrd, lwb_ack,) = [Signal(bool(0)) for _ in range(5)]
        wb.add_output_bus(lwb_do, lwb_ack)

        num_ackcyc = 1  # the number of cycle delays after cyc_i
        ackcnt = Signal(intbv(num_ackcyc, min=0, max=num_ackcyc+1))
        newcyc = Signal(bool(0))

        if self._debug:
            @instance 
            def debug_check():
                print("base address {:4X}, max address {:4X}".format(                
                    int(base_address), int(max_address)))
                while True:
                    assert clock is wb.clk_i is self.clock
                    assert reset is wb.rst_i is self.reset
                    yield clock.posedge
                    print("{:8d}: c:{}, r:{}, {} {} {} sel:{}, wr:{} n:{} "
                          "acnt {}, @{:04X}, i:{:02X} o:{:02X} ({:02X})".format(
                           now(), int(clock), int(reset),
                           int(wb.cyc_i), int(wb.we_i), int(wb.ack_o),
                           int(lwb_sel), int(lwb_wr),
                           int(newcyc), int(ackcnt), int(wb.adr_i),
                           int(wb.dat_i), int(wb.dat_o), int(lwb_do), ))

        @always_comb
        def beh_assign():
            lwb_acc.next = wb.cyc_i and wb.stb_i
            lwb_wr.next = wb.cyc_i and wb.stb_i and wb.we_i

        @always_seq(clock.posedge, reset=reset)
        def beh_selected():
            if (wb.cyc_i and wb.adr_i >= base_address and wb.adr_i < max_address):
                lwb_sel.next = True
            else:
                lwb_sel.next = False
                
        @always_seq(clock.posedge, reset=reset)
        def beh_bus_cycle():
            # set default, only active one cycle 
            newcyc.next = False     
            if wb.cyc_i:
                if ackcnt > 0:
                    ackcnt.next = ackcnt - 1
                    if ackcnt == 1:
                        newcyc.next = True
            else:
                ackcnt.next = num_ackcyc

        @always_comb
        def beh_ack():
            if wb.cyc_i and newcyc:
                lwb_ack.next = True
            else:
                lwb_ack.next = False

        # @todo: scan the register list, if it is contiguous remove
        #        the base and use the offset directly to access the
        #        register list instead of the for loop
        # if rf.contiguous:
        #     @always_seq(rb.clk_i.posedge, reset=rb.rst_i)
        #     def rtl_read():
        # else:

        # Handle a bus read (transfer the addressed register to the
        # data bus) and generate the register read pulse (let the
        # peripheral know the register has been read).
        # @always_seq(clock.posedge, reset=reset)
        @always_comb
        def beh_read():
            if lwb_sel and not lwb_wr and newcyc:
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
                        
        # Handle a bus write (transfer the data bus to the addressed
        # register) and generate a register write pulse (let the 
        # peripheral know the register has been written).
        @always(clock.posedge)
        def beh_write():
            if reset == int(reset.active):
                for ii in range(nregs):
                    ro = rol[ii]
                    dd = dl[ii]
                    if not ro:
                        regs_list[ii].next = dd
                    pwr[ii].next = False
            else:
                if lwb_wr and lwb_sel and newcyc:
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
        assign_inst = regfile.get_assigns()

        return myhdl.instances()

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def get_generic(self):
        generic = Barebone(Global(self.clock, self.reset),
                           data_width=self.data_width,
                           address_width=self.address_width)
        return generic

    @myhdl.block
    def map_to_generic(self, generic):
        clock = self.clock
        wb, bb = self, generic
        inprog = Signal(bool(0))

        # the output signals need to be local and then the "interconnect"
        # will combine all the outputs back to the master(s)
        lwb_do = Signal(intbv(0)[self.data_width:])
        lwb_ack = Signal(bool(0))
        wb.add_output_bus(lwb_do, lwb_ack)

        @always_comb
        def beh_assign():
            bb.write.next = wb.cyc_i and wb.we_i
            bb.read.next = wb.cyc_i and not wb.we_i
            bb.write_data.next = wb.dat_i
            lwb_do.next = bb.read_data
            bb.per_addr.next = wb.adr_i[:16]
            bb.mem_addr.next = wb.adr_i[16:]

        @always(clock.posedge)
        def beh_ack():
            if not lwb_ack and wb.cyc_i and not inprog:
                lwb_ack.next = True
                inprog.next = True
            elif lwb_ack and wb.cyc_i:
                lwb_ack.next = False
            elif not wb.cyc_i:
                inprog.next = False

        return beh_assign, beh_ack

    @myhdl.block
    def map_from_generic(self, generic):
        clock = self.clock
        wb, bb = self, generic
        inprog = Signal(bool(0))
        iswrite = Signal(bool(0))

        @always_comb
        def beh_assign():
            if bb.write or bb.read:
                wb.cyc_i.next = True
                wb.we_i.next = True if bb.write else False
            elif inprog:
                wb.cyc_i.next = True
                wb.we_i.next = True if iswrite else False
            else:
                wb.cyc_i.next = False
                wb.we_i.next = False

            wb.adr_i.next = concat(bb.per_addr, bb.mem_addr)
            wb.dat_i.next = bb.write_data
            bb.read_data.next = wb.dat_o

        @always(clock.posedge)
        def beh_delay():
            if not inprog and (bb.read or bb.write):
                inprog.next = True
                iswrite.next = bb.write
            if inprog and wb.ack_o:
                inprog.next = False
                iswrite.next = False

        @always_comb
        def beh_done():
            bb.done.next = not inprog

        return myhdl.instances()

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def writetrans(self, addr, val):
        """ write accessor for testbenches
        Not convertible.
        """
        self._start_transaction(write=True, address=addr, data=val)
        # toggle the signals for the bus transaction
        yield self.clk_i.posedge
        self.adr_i.next = addr
        self.dat_i.next = self._write_data
        self.we_i.next = True
        self.cyc_i.next = True
        self.stb_i.next = True
        to = 0
        # wait for ack
        while not self.ack_o and to < self.timeout:
            yield self.clk_i.posedge
            to += 1
        self.we_i.next = False
        self.cyc_i.next = False
        self.stb_i.next = False
        yield self.clk_i.posedge
        self._end_transaction()

    def readtrans(self, addr):
        """ read accessor for testbenches
        """
        self._start_transaction(write=False, address=addr)
        yield self.clk_i.posedge
        self.adr_i.next = addr
        self.cyc_i.next = True
        self.stb_i.next = True
        to = 0
        while not self.ack_o and to < self.timeout:
            yield self.clk_i.posedge
            to += 1
        self.cyc_i.next = False
        self.stb_i.next = False
        self._end_transaction(self.dat_o)

    def acktrans(self, data=None):
        """ acknowledge accessor for testbenches
        :param data:
        :return:
        """
        self.ack_o.next = True
        if data is not None:
            self.dat_o.next = data
        yield self.clk_i.posedge
        self.ack_o.next = False
