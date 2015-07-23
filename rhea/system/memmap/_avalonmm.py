#
# Copyright (c) 2014-2015 Christopher L. Felton
#

from __future__ import absolute_import

from myhdl import *
from rhea.system import Clock
from rhea.system import Reset
from ._memmap import MemMap


#@todo: Single controller interface
class AvalonMMController(object):
    def __init__(self, data_width=8, address_width=16):
        self.addr = Signal(intbv(0)[address_width:])
        self.wdata = Signal(intbv(0)[data_width:])
        self.rdata = Signal(intbv(0)[data_width:])
        self.read = Signal(bool(0))
        self.write = Signal(bool(0))
        self.done = Signal(bool(0))


class AvalonMM(MemMap):
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
        self._readatavalid.append(readdatavalid)
        self._waitrequest.append(waitrequest)


    def m_per_outputs(self):
        """ combine all the peripheral outputs
        """
        assert len(self._readdata) == len(self._readdatavalid)
        ndevs = len(self._readdata)

        av = self

        @always_seq(self.clk.posedge, reset=self.reset)
        def rtl_or_combine():
            rddats, valids, waits = 0, 0, 0
            for ii in range(ndevs):
                rddats = rddats | av._readdata[ii]
                valids = valids | av._readdatavalid[ii]
                waits = waits | av._waitrequest[ii]

            av.readdata.next = rddats
            av.readdatavalid.next = valids
            av.waitrequest.next = waits

        return rtl_or_combine


    def m_per_interface(self, glbl, regfile, name='', base_address=0x0):
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
        def rtl_selected():
            if av.address >= base_address and av.address <= max_address:
                selected.next = True
            else:
                selected.next = False

        # @todo: scan hte register list, if it is contiguous remove
        #        the base and use the offset directly to access the
        #        register list instead of the for loop
        # if regfile.contiguous:
        #     @always_seq(clock.posedge, reset=reset)
        #     ...

        # read side of the bus transaction
        @always(clock.posedge)
        def rtl_read():
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
        def rtl_write():
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
        gas = regfile.get_assigns()

        return instances()


    def get_controller_intf(self):
        return AvalonMMController(self.data_width, self.address_width)

            
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def m_controller_basic(self, ctl):
        """
        Bus controllers (master) are typically custom and
        built into whatever the controller is (e.g. a processor).
        This is a simple example with a simple interface to
        invoke bus cycles.

        :param ctl:
        :return:
        """
        av = self
        clock = av.clk
        reset = av.reset
        States = enum('Idle', 'Wait', 'Write', 'Read', 'ReadValid', 'Done')
        state = Signal(States.Idle)
        TOMAX = 33
        tocnt = Signal(intbv(0, min=0, max=TOMAX))

        @always_comb
        def assign():
            av.address.next = ctl.addr
            av.writedata.next = ctl.wdata
            ctl.rdata.next = av.readdata

        @always_seq(clock.posedge, reset=reset)
        def rtl():
            # ~~~[Idle]~~~
            if state == States.Idle:
                av.write.next = False
                av.read.next = False
                ctl.done.next = False
                if av.waitrequest:
                    state.next = States.Wait
                elif ctl.write:
                    state.next = States.Write
                elif ctl.read:
                    state.next = States.Read
                else:
                    ctl.done.next = True

            # ~~~[Wait]~~~
            elif state == States.Wait:
                if ctl.write:
                    av.write.next = True
                    av.read.next = False
                elif ctl.read:
                    av.write.next = False
                    av.read.next = True

                if not av.waitrequest:
                    tocnt.next = 0
                    if ctl.write:
                        state.next = States.Done
                    elif ctl.read:
                        state.next = States.ReadValid

            # ~~~[Write]~~~
            elif state == States.Write:
                av.write.next = True
                # @todo byteenables !!!
                state.next = States.Done
                tocnt.next = 0

            # ~~~[Read]~~~
            elif state == States.Read:
                av.read.next = True
                state.next = States.ReadValid

            # ~~~[ReadValid]~~~
            elif state == States.ReadValid:
                av.read.next = False
                if av.readdatavalid:
                    state.next = States.Done

            # ~~~[Done]~~~
            elif state == States.Done:
                ctl.done.next = True
                av.write.next = False
                av.read.next = False
                if not (ctl.write or ctl.read):
                    state.next = States.Idle

            else:
                assert False, "Invalid state %s" % (state,)

        return assign, rtl

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def write(self, addr, val):
        """ write accessor for testbenches
        :param addr: address to write
        :param val: value to write to the address
        :return: yields
        """
        self.wval = val
        yield self.clk.posedge
        self.address.next = addr
        self.writedata.next = val
        self.write.next = True
        to = 0
        while self.waitrequest and to < self.TIMEOUT:
            yield self.clk.posedge
            to += 1
        yield self.clk.posedge
        self.write.next = False
        yield self.clk.posedge
                      
    def read(self, addr):
        """ read accessor for testbenches
        :param addr:
        :return:
        """
        yield self.clk.posedge
        self.address.next = addr
        self.read.next = True
        to = 0
        while self.waitrequest and to < self.TIMEOUT:
            yield delay(1)
        self.read.next = False
        self.rval = self.readdata

    @property
    def readval(self):
        return self.rval