
from __future__ import absolute_import
from __future__ import print_function

from copy import deepcopy

from myhdl import Signal, intbv

from . import MemorySpace
from . import Register
from .._clock import Clock
from .._reset import Reset


# a count of the number of memory-map peripherals
_mm_per = 0
_mm_list = {}


class MemoryMapped(MemorySpace):
    def __init__(self, data_width, address_width):
        """ Base class for the different memory-map interfaces.
        This is a base class for the various memory-mapped (control and 
        status (CSR)) interfaces.  These interfaces all
        """
        super(MemoryMapped, self).__init__()
        self.data_width = data_width
        self.address_width = address_width
        self.names = {}
        self.regfiles = {}

        self.clock = Clock(bool(0))
        self.reset = Reset(0, active=1, async=False)

        # transaction information (simulation only)
        self._write = False    # write command in progress
        self._read = False     # read command in progress
        self._address = 0      # address of current/last transaction
        self._data = 0         # ??? @todo: is this used ???
        self._write_data = -1  # holds the data written
        self._read_data = -1   # holds the data read

        # bus transaction timeout in clock ticks
        self.timeout = 100
        
        # _debug is used to enable bus tracing prints etc.
        self._debug = False

    @property
    def is_write(self):
        return self._write

    @property
    def is_read(self):
        return self._read

    def get_read_data(self):
        return self._read_data

    def get_write_data(self):
        return self._write_data

    def get_address(self):
        return self._address

    def _start_transaction(self, write=False, address=None, data=None):
        self._write = write
        self._read = not write
        self._address = address
        if write:
            self._write_data = data
        else:
            self._read_data = data

    def _end_transaction(self, data=None):
        if self._read and data is not None:
            self._read_data = int(data)
        self._write = False
        self._read = False

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # public transactor API
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def write(self, addr, val):
        raise NotImplementedError

    def read(self, addr):
        raise NotImplementedError

    def ack(self, data=None):
        raise NotImplementedError

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # keep track of all the components on the bus
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def _add_bus(self, name):
        """ globally keep track of all per bus
        """
        global _mm_per, _mm_list
        nkey = "{:04d}".format(_mm_per) if name is None else name
        _mm_list[name] = self
        _mm_per += 1

    # @todo: make name and base_address attributes of regfile
    def add(self, glbl, regfile, name=''):
        """ add a peripheral register-file to the bus
        """
        # @todo: regfile should be replaced by `memspace` (MemorySpace) which
        # @todo: would be a simple object describing the address space occupied
        # @todo: and the RegisterFile would be a subclass. 
        # want a copy of the register-file so that the
        # address can be adjusted.
        arf = deepcopy(regfile)
        
        base_address = regfile.base_address
        # @todo: revisit the base_address assignment, the bus width needs
        # @todo: to be taken into account.
        if base_address is None:
            maxaddr = 0
            for k, v in self.regfiles.items():
                maxaddr = max(maxaddr, v.base_address)
            base_address = maxaddr + 0x100000
                
        for k, v in self.regfiles.items():
            if base_address == v.base_address:
                print("@E: Register file address collision")
                # @todo: raise an exception 

        for k, v in arf.__dict__.items():
            if isinstance(v, Register):
                v.addr += base_address

        if name in self.regfiles:
            self.names[name] += 1
            name = name.upper() + "_{:03d}".format(self.names[name])
        else:
            self.names = {name : 0}
            name = name.upper() + "_000"

        self.regfiles[name] = arf       

        # return the peripheral generators for this bus
        g = self.peripheral_regfile(glbl, regfile, name)
    
        return g

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # module (component) implementations
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def map_generic(self):
        """ Map this bus to the generic (Barebone) bus
        This is a bus adapter, it will adapt the 
        :return: generic bus, myhdl generators
        """
        raise NotImplementedError

    def map_

    def peripheral_regfile(self, glbl, regfile, name, base_address=0):
        """ override
        :param glbl: global signals, clock and reset
        :param regfile: register file interfacing to.
        :param name: name of this interface
        :param base_address: base address for this register file
        :return: myhdl generators
        """
        raise NotImplementedError

    def interconnect(self):
        """ Connect all the components
        """
        raise NotImplementedError


