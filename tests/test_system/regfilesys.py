
"""
This modules defines a component with a complex register file, loosely
based off the "gemac_simple" core [1].  

[1]: @todo: background on the core 
"""

from __future__ import print_function, division

import myhdl
from myhdl import Signal, intbv, always_comb, concat

from rhea import Global, Clock, Reset
from rhea.system import Register, RegisterFile
from rhea.system import Barebone, Wishbone, AvalonMM, AXI4Lite


def build_regfile():
    """ Build a register file definition.
    This register file definition is loosely based off the gemac_simple ... 
    """
    regfile = RegisterFile()
    for ii in range(2):
        reg = Register(name='macaddr{}'.format(ii), width=32, access='rw', default=0)
        regfile.add_register(reg)   
    
    for ii, dd in enumerate((0xFFFFFFFF, 0xFFFFFFFF)):
        reg = Register(name='ucastaddr{}'.format(ii), width=32, access='rw', default=dd)
        regfile.add_register(reg)

    for ii, dd in enumerate((0xFFFFFFFF, 0xFFFFFFFF)):
        reg = Register(name='mcastaddr{}'.format(ii), width=32, access='rw', default=dd)
        regfile.add_register(reg)
        
    reg = Register(name='control', width=32, access='rw', default=0)
    # @todo: add the named bits
    
    regfile.add_register(reg)
    
    return regfile


@myhdl.block
def memmap_component(glbl, csrbus, cio, user_regfile=None):
    """
    Ports
    -----
    :param glbl: global signals, clock, reset, enable, etc.
    :param csrbus: memory-mapped bus 
    :param cio: component IO 
    :param user_regfile:
    """
    if user_regfile is None:
        regfile = build_regfile()
    else:
        regfile = user_regfile
        
    regfile_inst = csrbus.add(glbl, regfile, name='TESTREG')

    @always_comb
    def beh_assign():
        s = concat(regfile.macaddr0[:2], regfile.control[6:])
        cio.next = s

    return regfile_inst, beh_assign


@myhdl.block
def regfilesys(clock, reset):
    """
    """
    glbl = Global(clock, reset)
    csrbus = AXI4Lite(glbl, data_width=32, address_width=32)
    cio = Signal(intbv(0)[8:])
    
    mminst = memmap_component(glbl, csrbus, cio)
    
    return mminst

