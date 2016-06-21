
from __future__ import print_function, absolute_import

from copy import deepcopy
import myhdl
from ..clock import Clock
from ..reset import Reset
from ..cso import ControlStatusBase

from . import MemorySpace
from . import RegisterFile, Register


# a count of the number of memory-map peripherals
_mm_per = 0
_mm_list = {}


class MemoryMap(list):
    def __init__(self):
        """ Contains a collection of MemoryMapped objects
        When a system is defined with numerous modules connect via a
        memory-mapped bus this object is used to manage the complete
        collection.
        """
        super(list, self).__init__()


class MemoryMapped(MemorySpace):
    def __init__(self, glbl=None, data_width=8, address_width=16):
        """ Base class for the different memory-map interfaces.
        This is a base class for the various memory-mapped (control and 
        status (CSR)) interfaces.
        """
        super(MemoryMapped, self).__init__()
        self.data_width = data_width
        self.address_width = address_width
        self.names = {}
        self.regfiles = {}

        if glbl is None:
            self.clock = Clock(bool(0))
            self.reset = Reset(0, active=1, async=False)
        else:
            self.clock, self.reset = glbl.clock, glbl.reset

        # transaction information (simulation only)
        self._write = False    # write command in progress
        self._read = False     # read command in progress
        self._address = 0      # address of current/last transaction
        self._data = 0         # ??? @todo: is this used ???
        self._write_data = -1  # holds the data written
        self._read_data = -1   # holds the data read

        self.num_peripherals = 0
        self.num_controllers = 0

        # bus transaction timeout in clock ticks
        self.timeout = 100

        # the generic shadow of this bus, each
        self.generic = None
        
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
    def writetrans(self, addr, data):
        """ Write transaction """
        raise NotImplementedError

    def readtrans(self, addr):
        """ Read transaction """
        raise NotImplementedError

    def acktrans(self, data=None):
        """ Acknowledge transaction """
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

    @myhdl.block
    def add(self, memspace, name=''):
        """ add a peripheral register-file to the bus
        """
        assert isinstance(memspace, MemorySpace)
        self.num_peripherals += 1
        base_address = memspace.base_address

        if isinstance(memspace, RegisterFile):
            regfile = memspace
            # want a copy of the register-file so that the
            # address can be adjusted.
            arf = deepcopy(regfile)

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

            # automatically assigning an empty base_address
            memspace.base_address = base_address

            for k, v in arf.__dict__.items():
                if isinstance(v, Register):
                    v.addr += base_address

            if name in self.regfiles:
                self.names[name] += 1
                name = name.upper() + "_{:03d}".format(self.names[name])
            else:
                self.names = {name: 0}
                name = name.upper() + "_000"

            self.regfiles[name] = arf

            # return the peripheral generators for this bus
            g = self.peripheral_regfile(regfile, name)

        else:
            if base_address is None:
                memspace.base_address = self.num_peripherals
            # @todo: complete, add the non-regfile to the bus
            g = []
    
        return g

    # @todo: remove `add_csr` and replace with
    # @todo:     rf = cso.build_register_file()
    # @todo:     mmbus.add(rf)
    def add_csr(self, csr, name=''):
        """
        """
        assert isinstance(csr, ControlStatusBase)

        # the `csr` objects are void of any memory-map specific information
        # the "mapping" all occurs here.
        # @todo: refactor, shares code with above ???
        maxaddr = 0
        for k, v in self.regfiles.items():
            maxaddr = max(maxaddr, v.base_address)
        base_address = maxaddr + 0x100000

        for k, v in self.regfiles.items():
            if base_address == v.base_address:
                print("@E: Register file address collision")
                # @todo: raise an exception

        # create a memspace / register file for this csr
        dw = self.data_width
        memspace = RegisterFile()


    # @todo: add `add_master` (`add_controller`), adds master/controller
    # @todo: to the bus.

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # module (component) implementations
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def get_generic(self):
        """ Get the generic bus interface
        Return the object that map_to_generic maps to.
        :return: generic bus interface
        """
        raise NotImplementedError

    def map_to_generic(self, generic):
        """ Map this bus to the generic (Barebone) bus
        This is a bus adapter, it will adapt the
        :return: generic bus, myhdl generators
        """
        raise NotImplementedError

    def map_from_generic(self, generic):
        """ Map the generic bus (Barebone) to this bus
        This is a bus adapter that will adapt the generic bus to this
        bus.  This is a module and returns myhdl generators

        Arguments
        ---------
        generic: The generic memory-mapped bus, all the memory-mapped
        supported modules use the *generic* bus internally.  This provides
        an agnostic bus interface to all the modules.

        Returns
        -------
        myhdl generators
        """
        raise NotImplementedError

    def peripheral_regfile(self, regfile, name, base_address=0):
        """ override

        Arguments
        ---------
        glbl: global signals, clock and reset
        regfile: register file interfacing to

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


