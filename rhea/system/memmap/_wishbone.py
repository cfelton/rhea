#
# Copyright (c) 2014-2015 Christopher L. Felton
#

from __future__ import absolute_import

from myhdl import *

from .. import Clock
from .. import Reset

from . import MemMap
from . import Barebone


class Wishbone(MemMap):
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
        # _o and _i on many of the signals.  Preserved the
        # peripheral (slave) point of view names.
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

        al, rl, rol, dl = rf.get_reglist()
        addr_list, regs_list = al, rl
        pwr, prd = rf.get_strobelist()

        nregs = len(regs_list)
        max_address = base_address + max(addr_list)

        lwb_do = Signal(intbv(0)[self.data_width:])
        (lwb_sel,lwb_acc,lwb_wr,
         lwb_wrd,lwb_ack,) = [Signal(bool(0)) for ii in range(5)]
        wb.add_output_bus(name, lwb_do, lwb_ack)

        ACNT = 1
        ackcnt = Signal(intbv(ACNT, min=0, max=ACNT+1))
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
        #        register list instead of the for loop
        # if rf.contiguous:
        #     @always_seq(rb.clk_i.posedge, reset=rb.rst_i)
        #     def rtl_read():
        # else:

        # @todo
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
        return Barebone(self.data_width, self.address_width)

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def map_generic(self, generic):
        wb = self

        @always_comb
        def rtl_assign():
            if generic.write or generic.read:
                wb.cyc_i.next = True
                wb.we_i.next = True if generic.write else False

            wb.adr_i.next = concat(generic.per_addr, generic.reg_addr)

            generic.ack = wb.ack_o


        return rtl_assign

    # @todo: remove this ???
    def m_controller(self, ctl):
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
        Not convertible.
        """
        self._start_transaction(write=True, address=addr, data=val)
        # toggle the signals for the bus transaction
        yield self.clk_i.posedge
        self.adr_i.next = addr
        self.dat_i.next = self.wval
        self.we_i.next = True
        self.cyc_i.next = True
        self.stb_i.next = True
        to = 0
        # wait for ack
        while not self.ack_o and to < self.timeout:
            yield self.clk_i.posedge   # was delay(1)
            to += 1
        self.we_i.next = False
        self.cyc_i.next = False
        self.stb_i.next = False
        yield self.clk_i.posedge
        self._end_transaction()

    def read(self, addr):
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

    def ack(self, data=None):
        """ acknowledge accessor for testbenches
        :param data:
        :return:
        """
        self.ack_o.next = True
        if data is not None:
            self.dat_o.next = data
        yield self.clk_i.posedge
        self.ack_o.next = False


# -----------------------------------------------------------------------------
def m_controller(generic, memmap):
    """ Generic memap interface to Wishbone controller

    :return: myhdl generators
    """
    assert isinstance(generic, Barebone)
    assert isinstance(memmap, MemMap)
    raise NotImplementedError


def m_peripherial(memmap, generic):
    """ Wishbone to generic memmap interface

    Ports
    -----
      gen:
      memmap:

    :return: myhdl generators
    """
    assert isinstance(memmap, MemMap)
    assert isinstance(generic, Barebone)
    raise NotImplementedError
