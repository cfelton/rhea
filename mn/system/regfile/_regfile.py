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
from myhdl._Signal import _Signal
from myhdl import SignalType

_width = None

class RegisterBits(object):
    def __init__(self, name, slc, comment=""):
        self.name = name     # name of the bits
        self.b = slc         #
        self.comment = comment

    def __getitem__(self, k):
        return self.__dict__[k]

# a register should be a list of signals (specifically a list
# of Signal(bool).  If a subset of the register is an int or
# the full is an int it needs to be casted to an integer before
# using.
class Register(_Signal):
    """
    This class contains all the information about a register in a 
    register file.  There are two types are registers: read-write
    'rw' and read-only 'ro'.  The 'rw' registers can only be modified
    by the memory-map (memmap) interface and can have read named bits.
    The 'ro' registers can only be modified by the peripheral.
    """

    def __init__(self, name, addr, width, access='rw', default=0, comment=""):
        global _width
        _Signal.__init__(self,intbv(default)[width:])

        self._nmb = [None for ii in range(width)]  # hold the named-bits

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

        if _width is None:
            _width = width
        else:
            assert width == _width, "All registers must be the same width"

    def __copy__(self):
        reg = Register(self.name, self.addr, self.width, self.access,
                       self.default, self.comment)
        for k,v in self.bits.iteritems():
            reg.add_named_bits(k, v.b, v.comment)
        return reg

    def __deepcopy__(self, memo):
        return self.__copy__()

    def add_named_bits(self, name, slc, comment=""):
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

    def m_assign(self):
        """ assign the named 'ro' bits to the register """

        # check for any missing bits and add a stub
        # @todo: ? create warning for missing bits, these 
        #    will be dangling ?
        for ii, namedbits in enumerate(self._nmb):
            # if a namedbit does not exist stub it out
            if not isinstance(namedbits, SignalType):                
                self._nmb[ii] = Signal(bool(self[ii]))
                
        wbits = self._nmb
        nbits = self.width
        @always_comb
        def rtl_assign():
            for ii in range(nbits):
                self.next[ii] = wbits[ii]

        return rtl_assign


class RegisterFile(object):

    def __init__(self, regdef=None):
        """
        Arguments
        ---------
        regdef : register file dictionary definition        
        
        """
        self._rwregs = []  # read-write registers
        self._roregs = []  # read-only registers
        self.registers = {}

        # @todo: if the regdef is dict-of-dict definiton, first
        #    build the registers
        if regdef is not None:
            for k,v in regdef.iteritems():
                if isinstance(v, Register):
                    self.registers[k] = v
            
        self._allregs = None
        
        #@todo: sort the regdef by lowest address to highest address.
        
        # The registers can be defined in two methods, a dict defintion
        # that conforms to a particular structure or using the Register
        # object (the dict method is not implemented yet).
        if regdef is not None:
            for k,v in regdef.iteritems():
                self._append_register(k, v)

    @property
    def roregs(self):
        return self._roregs

    @property
    def rwregs(self):
        return self._rwregs

    def _append_register(self, name, reg):
        """ append a register to the list 
        """
        if isinstance(reg, dict):
            # @todo: _check_register_def
            # reg = Register(reg['name'],...)
            raise NotImplementedError("dict description TBC");
        if not isinstance(reg, Register):
            raise ValueError("Invalid type in regdef %s"%(type(reg)))
                             
        self.__dict__[name] = reg
        if reg.access == 'rw':  # @todo: remove or reg['access'] == 'wt':
            self._rwregs.append((reg.addr, reg,))
        elif reg.access == 'ro':
            self._roregs.append((reg.addr, reg,))

        # create a reference to the named bits, all named bits 
        # will be accessible from the regfile
        for kb,vb in reg.bits.iteritems():
            if self.__dict__.has_key(kb):
                raise StandardError("bit(s) name, %s, already exists"%(kb))
            self.__dict__[kb] = reg.__dict__[kb]


    def add_register(self, reg):
        """ add a register to the register file """
        assert not self.registers.has_key(reg.name)
        self.registers[reg.name] = reg
        self._append_register(reg.name, reg)


    def get_reglist(self):
        """ return a list of addresses and a list of registers.        
        """
        rwa = [aa for aa,rr in self._rwregs]       # rw address
        rwr = [rr for aa,rr in self._rwregs]       # rw register
        _rrw = [False for aa,rr in self._rwregs]
        roa = [aa for aa,rr in self._roregs]       # ro address
        ror = [rr for aa,rr in self._roregs]       # ro register
        _rro = [True for aa,rr in self._rwregs]
        self._allregs = rwr+ror
        dl = [rr.default for aa,rr in self._rwregs+self._roregs]
        #@todo: order the list from low address to high address
        #@todo: set flag if addresses are contiguous
        return (tuple(rwa+roa),rwr+ror,tuple(_rrw+_rro),tuple(dl))


    def get_strobelist(self):
        assert self._allregs is not None
        wr = [rr.wr for rr in self._allregs]
        rd = [rr.rd for rr in self._allregs]
        return wr,rd


    #def get_readonly(self, name=None, addr=None):
    #    roreg = None
    #    if name is not None:
    #        if self._regdef is None:
    #            # @todo: need to search for the name
    #            raise NotImplemented
    #        else:
    #            addr = self._regdef[name].addr
    #    assert addr is not None
    #    for aa,rr in self._roregs:
    #        print(aa,rr)
    #        if addr == aa:
    #            roreg = rr
    #            break
    #    assert roreg is not None, "Invalid register %s %x"%(name,addr)
    #    return roreg
    
    # @todo: remove, use regbus.add/regbus.m_per_interface
    # def m_per_interface(self, clock, reset, regbus,
    #                     name = '',
    #                     base_address = 0x00):
    #     """ Memory-mapped peripheral interface
    #     The register bus access to the register file, external
    #     to the module reads and writes.
    #
    #     """
    #
    #     # @todo: use *glbl* and figure out *args*
    #     # get the memmap bus specific read/write
    #     busi = regbus.m_per_interface(clock, reset,
    #                                   regfile=self,
    #                                   name=name,
    #                                   base_address=base_address)
    #
    #     # get the generators that assign the named-bits
    #     gas = []
    #     for aa,rr in self._roregs:
    #         gas += [rr.m_assign()]
    #
    #     return busi, gas

    def get_assigns(self):
        gas = []
        for aa,rr in self._roregs:
            gas += [rr.m_assign()]
        return gas
