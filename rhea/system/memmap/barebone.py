#
# Copyright (c) 2014-2015 Christopher L. Felton
#

from __future__ import print_function, absolute_import

from math import log, ceil
import myhdl
from myhdl import Signal, intbv
from .memmap import MemoryMapped


class Barebone(MemoryMapped):
    name = 'barebone'

    def __init__(self, glbl, data_width=8, address_width=8,
                 name=None, num_peripherals=16):
        """ Generic memory-mapped interface.

        This interface is the "generic" and most basic memory-map
        interface.  This can be used for a common bus but also limited
        functionality bus.  A bus cycle is instigated with a `write`
        or `read` strobe.  The `write` and `read` strobes should
        only be asserted if the `done` signal is active (high). As
        soon as the peripheral (slave) detects the read or write
        strobe the done signals will go low and remain low until
        the slave has completed the transaction.

        The done signals indicates two states, that the slave has
        finished any previous operations and that it is ready to
        retrieve any new operations.  A master can pulse the write
        or read at anytime the done signals is active, the slave
        will process one or more writes (up to max_burst).  At that
        point the master needs to relinquish and wait for done.

        The address bus is separated into two separate address buses,
        peripheral address (`per_addr`, select a component/peripheral)
        and the memory address (`mem_addr`).  The `per_addr` is used
        to select a peripheral and the `mem_addr` is used to access
        the memory-space in the peripheral.

        The Barebone bus is point-to-point, only a single master
        and slave can be connected to a bus.  The interconnect is
        used to enable multiple slaves and masters

        Timing Diagram
        ---------------
        clock       /--\__/--\__/--\__/--\__/--\__/--\__/--\__/--\__
        reset       /-----\_________________________________________
        write       ____________/-----\_____________________________
        read        _____________________________/------\___________
        *valid      ____________________________________/-----\_____
        done        ------------\______/---------\____________/-----
        read_data   -----------------------------|read data |-------
        write_data  ------------|write data |-----------------------
        per_addr
        mem_addr    ------------\write addr |----|read addr |-------

        * currently not implemented but envisioned it will be added

        (arguments == ports)
        Arguments:
            glbl: system clock and reset
            data_width: data bus width
            address_width: address bus width
            name: name for the bus
            num_peripherals: the number of peripherals targetted
        """        
        super(Barebone, self).__init__(glbl,
                                       data_width=data_width,
                                       address_width=address_width)
        self.write = Signal(bool(0))
        self.read = Signal(bool(0))
        # @todo: replace "ack" with "done" (?)
        self.done = Signal(bool(1))
        self.read_data = Signal(intbv(0)[data_width:])
        self.write_data = Signal(intbv(0)[data_width:])

        # separate address bus for selecting a peripheral and the register
        # addresses.  The total number of peripherals is num_periphal-1,
        # the max address (all 1s) is reserved to indicate "done" (idle)
        pwidth = int(ceil(log(float(num_peripherals), 2)))
        self.per_addr = Signal(intbv(0)[pwidth:])
        self.mem_addr = Signal(intbv(0)[address_width-pwidth:])
        self.address = self.mem_addr

        self.max_burst = 16

    def add_output_bus(self, read_data, done):
        pass

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Transactors
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def writetrans(self, addr, data):
        self._start_transaction(write=True, address=addr, data=data)
        # @todo: this will need to be enhanced for multiple master
        # @todo: scenario, wait for done vs. asserting done
        assert self.done
        print("Barebone: write transaction {:08X} to {:08X}".format(data, addr))
        self.write.next = True
        self.write_data.next = data
        self.mem_addr.next = addr
        to = 0
        yield self.clock.posedge
        self.write.next = False
        yield
        while not self.done and to < self.timeout:
            yield self.clock.posedge
            to += 1
        self.write_data.next = 0
        self._end_transaction(self.write_data)

    def readtrans(self, addr):
        self._start_transaction(write=False, address=addr)
        assert self.done
        print("Barebone: read transaction to {:08X}".format(addr), end='')
        self.read.next = True
        self.mem_addr.next = addr
        to = 0
        yield self.clock.posedge
        self.read.next = False
        rd = int(self.read_data)
        while not self.done and to < self.timeout:
            rd = int(self.read_data)
            yield self.clock.posedge
            to += 1
        print(" read {:08X}".format(rd))
        self._end_transaction(rd)

    def acktrans(self, data=None):
        self.done.next = False
        if data is not None:
            self.read_data.next = data
        yield self.clock.posedge
        self.done.next = True

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Modules
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def get_generic(self):
        return self

    def map_to_generic(self, generic):
        """
        In this case *this* is the generic bus, there is no mapping that
        needs to be done.  Simply return ourself and all is good.
        """
        return []

    def map_from_generic(self, generic):
        """
        In this case the *this* is the generic bus, use the signals
        passed, that is the expected behavior.

        Arguments:
            generic: the generic bus to map from
        """
        self.write = generic.write
        self.read = generic.read
        self.write_data = generic.write_data
        self.read_data = generic.read_data
        self.done = generic.done
        self.per_addr = generic.per_addr
        self.mem_addr = generic.mem_addr

        return []

    def peripheral_regfile(self, glbl, regfile, name, base_address=0):
        """
        (arguments == ports)
        Arguments:
            glbl: global signals, clock, reset, enable, etc.
            regfile: register file
            name:
            base_address:
        """
        return []

    def interconnect(self):
        """
        :return:
        """

        return []
