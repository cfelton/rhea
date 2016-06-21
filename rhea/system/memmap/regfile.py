#
# Copyright (c) 2006-2013 Christopher L. Felton
#

from copy import deepcopy

import myhdl
from myhdl import Signal, intbv, always_comb
from myhdl import SignalType

from ..cso import ControlStatusBase
from . import MemorySpace


class RegisterBits(object):
    def __init__(self, name, slc, comment=""):
        self.name = name     # name of the bits
        self.b = slc         #
        self.comment = comment

    def __getitem__(self, k):
        return self.__dict__[k]


class Register(SignalType):
    def __init__(self, name, width, access='rw', default=0,
                 addr=None, comment=""):
        """
        This class contains all the information about a register in a 
        register file.  There are two types are registers: read-write
        'rw' and read-only 'ro'.  The 'rw' registers can only be modified
        by the memory-map (memmap) interface and can have read named bits.
        The 'ro' registers can only be modified by the peripheral.
        """

        super(Register, self).__init__(intbv(default)[width:])

        self._nmb = [None for _ in range(width)]  # hold the named-bits

        self.name = name            # the name of the register
        self.addr = addr            # address of the register
        self.width = width          # width of the register 
        self.access = access        # access type, 'rw' or 'ro'
        self.default = default      # default value for this register
        self.comment = comment      # a comment for this register
        self.bits = {}              # dict with namedbits Signals
        self.rfidx = -1             # index in the regfile list
        self.has_namedbits = False  # this register has named bits

        # @todo: are these used ?
        # the register read and write strobes to the peripheral        
        self.wr = Signal(bool(0))
        self.rd = Signal(bool(0))

    def __copy__(self):
        reg = Register(self.name, self.width, self.access,
                       self.default, self.addr,  self.comment)
        for k, v in self.bits.items():
            reg.add_namedbits(k, v.b, v.comment)
        return reg

    def __deepcopy__(self, memo):
        return self.__copy__()

    def add_namedbits(self, name, bits, comment=""):
        """ Add a named bit
        A named bit allows named access to a bit

            reg = Regsiter()
            #...
            if reg.enable
            # ...

        Where `reg.enable` might be bit reg[0].  For read-write (rw)
        registers (read-write from the controllers perspective) named bits
        are read-only on the peripheral side and read-only (ro) registers
        named bits are read-write.  For the read-only register (rw nmb)
        a copy of the signals is created.

        :param name:
        :param bits:
        :param comment:
        :return:
        """
        if isinstance(bits, int):
            slc = slice(bits+1, bits)
        elif isinstance(bits, tuple):
            slc = slice(bits[0], bits[1])
        elif isinstance(bits, slice):
            slc = bits
        else:
            raise ValueError("Incorrect bits argument: {} {}".format(
                type(bits), bits))

        bits = RegisterBits(name, slc, comment)
        self.bits[bits.name] = bits

        if self.access == 'rw':
            self.__dict__[bits.name] = self(slc)
        elif self.access == 'ro':
            w = slc.start-slc.stop
            ival = self[slc.start:slc.stop]
            nmb = Signal(intbv(ival)[w:]) 
            self.__dict__[bits.name] = nmb
            
            # _nmb (named-bits) is a one for one list of Signals,
            # each signal in the _nmb will be assigned to the register.
            for idx in range(slc.stop, slc.start):   
                if self._nmb[idx] is not None:
                    print("@W: overwritting namedbit %d" % (idx,))
                self._nmb[idx] = nmb(idx-slc.stop)
        else:
            raise TypeError

    @myhdl.block
    def assign_namedbits(self):
        """ assign the named 'ro' bits to the register """

        # check for any missing bits and add a stub
        # @todo: ? create warning for missing bits, these will 
        # @todo: be dangling ?
        for ii, namedbits in enumerate(self._nmb):
            # if a namedbit does not exist stub it out
            if not isinstance(namedbits, SignalType):                
                self._nmb[ii] = Signal(bool(self[ii]))

        # local references (sane names for generator)
        wbits = self._nmb
        nbits = self.width

        @always_comb
        def beh_assign():
            for ii in range(nbits):
                self.next[ii] = wbits[ii]

        return beh_assign


class RegisterFile(MemorySpace):
    def __init__(self, regdef=None):
        """
        
        Arguments
        ---------
        regdef : register file dictionary definition        
        
        
        """
        super(RegisterFile, self).__init__()

        self._offset = 0           # current register offset`
        self._rwregs = []          # read-write registers
        self._roregs = []          # read-only registers
        self.registers = {}        # collection of all registers added
        
        # @todo: if the regdef is dict-of-dict definition, first
        # @todo: build the registers
        
        # register is a name, register dictionary
        if regdef is not None:
            for k, v in regdef.items():
                if isinstance(v, Register):
                    self.registers[k] = v
            
        self._allregs = None
        
        #@todo: sort the regdef by lowest address to highest address.
        
        # The registers can be defined in two methods, a dict defintion
        # that conforms to a particular structure or using the Register
        # object (the dict method is not implemented yet).
        if regdef is not None:
            for k, v in regdef.items():
                self._append_register(k, v)

    @property
    def roregs(self):
        return self._roregs

    @property
    def rwregs(self):
        return self._rwregs

    def get_regdef(self):
        regdef = {}
        for k, v in self.__dict__.items():
            if isinstance(v, Register):
                regdef[k] = deepcopy(v)

        return regdef

    def _append_register(self, name, reg):
        """ append a register to the list 
        """
        # if an address is given generate one, this will be adjusted
        # when all the register files are combined on a bus
        if reg.addr is None:
            reg.addr = self._offset
            self._offset += 4
        else:
            self._offset = reg.addr + 4

        if isinstance(reg, dict):
            # @todo: _check_register_def
            # reg = Register(reg['name'],...)
            raise NotImplementedError("dict description TBC");
        if not isinstance(reg, Register):
            raise ValueError("Invalid type in regdef {}".format(type(reg)))
                             
        self.__dict__[name] = reg
        if reg.access == 'rw':  # @todo: remove or reg['access'] == 'wt':
            self._rwregs.append((reg.addr, reg,))
        elif reg.access == 'ro':
            self._roregs.append((reg.addr, reg,))

        # create a reference to the named bits, all named bits 
        # will be accessible from the regfile
        for kb, vb in reg.bits.items():
            if kb in self.__dict__:
                raise Exception("bit(s) name, {}, already exists".format(kb))
            self.__dict__[kb] = reg.__dict__[kb]

    def add_register(self, reg):
        """ add a register to the register file """
        assert reg.name not in self.registers
        self.registers[reg.name] = reg
        self._append_register(reg.name, reg)

    def get_reglist(self):
        """ return a list of addresses and a list of registers.        
        """
        rwa = [aa for aa, rr in self._rwregs]       # rw address
        rwr = [rr for aa, rr in self._rwregs]       # rw register
        _rrw = [False for aa, rr in self._rwregs]
        roa = [aa for aa, rr in self._roregs]       # ro address
        ror = [rr for aa, rr in self._roregs]       # ro register
        _rro = [True for aa, rr in self._rwregs]
        self._allregs = rwr+ror
        dl = [rr.default for aa,rr in self._rwregs+self._roregs]
        # @todo: order the list from low address to high address
        # @todo: set flag if addresses are contiguous
        return tuple(rwa+roa), rwr+ror, tuple(_rrw+_rro), tuple(dl)

    def get_strobelist(self):
        assert self._allregs is not None
        wr = [rr.wr for rr in self._allregs]
        rd = [rr.rd for rr in self._allregs]
        return wr, rd

    @myhdl.block
    def get_assigns(self):
        assign_inst = []
        for aa, rr in self._roregs:
            assign_inst += [rr.assign_namedbits()]
        return assign_inst


def build_register_file(cso):
    """ Build a register file from a control-status object.

    This function will organize all the `SignalType` attributes in
    a `ControlStatus` object into a register file.

    This function implementation is incomplete.
    """
    assert isinstance(cso, ControlStatusBase)
    rf = RegisterFile()

    for k, v in vars(cso):
        if isinstance(v, SignalType):
            pass

    return rf
