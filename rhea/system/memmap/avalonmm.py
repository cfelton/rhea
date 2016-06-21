#
# Copyright (c) 2014-2015 Christopher L. Felton
#

from __future__ import absolute_import

import myhdl
from myhdl import (Signal, intbv, always_seq, always, always_comb,
                   instances, enum, delay, concat)

from .. import Clock
from .. import Reset
from . import MemoryMapped
from . import Barebone


class AvalonMM(MemoryMapped):
    name = 'avalon'

    def __init__(self, glbl=None, data_width=8, address_width=16, name=None):
        """ AvalonMM bus object
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

        self._readdata = []
        self._readdatavalid = []
        self._waitrequest = []
        # @todo: _response ???

    def add_output_bus(self, name, readdata, readdatavalid, waitrequest):
        self._readdata.append(readdata)
        self._readdatavalid.append(readdatavalid)
        self._waitrequest.append(waitrequest)

    @myhdl.block
    def interconnect(self):
        """ combine all the peripheral outputs
        """
        assert len(self._readdata) == len(self._readdatavalid)
        ndevs = len(self._readdata)
        av = self

        @always_seq(self.clk.posedge, reset=self.reset)
        def beh_or_combine():
            rddats, valids, waits = 0, 0, 0
            for ii in range(ndevs):
                rddats = rddats | av._readdata[ii]
                valids = valids | av._readdatavalid[ii]
                waits = waits | av._waitrequest[ii]

            av.readdata.next = rddats
            av.readdatavalid.next = valids
            av.waitrequest.next = waits

        return beh_or_combine

    @myhdl.block
    def peripheral_regfile(self, regfile, name='', base_address=0x0):
        """ memory-mapped avalon peripheral interface
        """

        # local alias
        av = self      # register bus
        rf = regfile   # register file definition

        # get the list-of-signals that represent the regfile
        al, rl, rol, dl = rf.get_reglist()
        addr_list, regs_list = al, rl
        pwr, prd = rf.get_strobelist()

        # @todo: have be base_address be an attribute of the regfile
        nregs = len(regs_list)
        max_address = base_address + max(addr_list)

        # @todo: add the peripheral interface stuff ...

        clock = self.clk
        reset = self.reset

        # determine if this register-file is selected, this check
        # adds an extra clock cycle to the transaction
        selected = Signal(bool(0))

        @always_seq(clock.posedge, reset=reset)
        def beh_selected():
            if av.address >= base_address and av.address < max_address:
                selected.next = True
            else:
                selected.next = False

        # @todo: scan the register list, if it is contiguous remove
        #        the base and use the offset directly to access the
        #        register list instead of the for loop
        # if regfile.contiguous:
        #     @always_seq(clock.posedge, reset=reset)
        #     ...

        # read side of the bus transaction
        @always(clock.posedge)
        def beh_read():
            if reset == int(reset.active):
                for ii in range(nregs):
                    prd[ii].next = False
            else:
                if selected and not av.write:
                    for ii in range(nregs):
                        aa = addr_list[ii]
                        aa = aa + base_address
                        if av.address == aa:
                            av.readdata.next = regs_list[ii]
                            prd[ii].next = True
                else:
                    av.readdata.next = 0
                    for ii in range(nregs):
                        prd[ii].next = False

        # write side of the bus transaction
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
                if selected and av.write:
                    for ii in range(nregs):
                        aa = addr_list[ii]
                        aa = aa + base_address
                        ro = rol[ii]
                        if not ro and av.address == aa:
                            regs_list[ii].next = av.writedata
                            pwr[ii].next = True
                else:
                    for ii in range(nregs):
                        pwr[ii].next = False

        # get the generators that assign the named bits
        assign_insts = regfile.get_assigns()

        return myhdl.instances()

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # @todo: map_to_generic(self)
    # @todo: map_from_generic(self, generic)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def writetrans(self, addr, val):
        """ write accessor for testbenches
        :param addr: address to write
        :param val: value to write to the address
        :return: yields
        """
        self._start_transaction(write=True, address=addr, data=val)
        self.address.next = addr
        self.writedata.next = val
        self.write.next = True
        to = 0
        while self.waitrequest and to < self.timeout:
            yield self.clock.posedge
            to += 1
        yield self.clock.posedge
        self.write.next = False
        self.writedata.next = 0
        self._end_transaction(self.writedata)
                      
    def readtrans(self, addr):
        """ read accessor for testbenches
        :param addr:
        :return:
        """
        self._start_transaction(write=False, address=addr)
        self.address.next = addr
        self.read.next = True
        to = 0
        while self.waitrequest and to < self.timeout:
            yield self.clock.posedge
        self.read.next = False
        self._end_transaction(self.readdata)

    def acktrans(self, data=None):
        self.readdatavalid.next = True
        if data is not None:
            self.readdata.next = data
        yield self.clock.posedge
        self.readdatavalid.next = False
