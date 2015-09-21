

from __future__ import print_function
from __future__ import division

"""
This modules defienes a component with a complex reigster file, loosely
based off the "gemac_simple" core [1].  

[1]: @todo: background on the core 
"""

from rhea.system import Global
from rhea.system import RegisterFile
from rhea.system import Register 
from rhea.system import Barebone, Wishbone, Avalon, AXI4Lite


def build_regfile():
    """ Build a register file definition.
    This register file definition is loosely based off the gemac_simple ... 
    """
    regfile = RegisterFile(width=32)
    for ii in range(2):
        reg = Register(name='macaddr{}'.format(ii), access='rw', defalut=0)
        regfile.add_register(reg)   
    
    for ii, dd in enumerate((,)):
        reg = Register(name='ucastaddr{}'.format(ii), access='rw', default=dd)
        regfile.add_register(reg)

    for ii, dd in enumerate((,)):
        reg = Register(name='mcastaddr{}'.format(ii), access='rw', default=dd)
        regfile.add_register(reg)
        
    reg = Register(name='control', access'rw', default=0)
    # @todo: add the named bits
    regfile.add_register(reg)


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
    greg = csrbus.add(regfile)
    
    
    return greg


def regfilesys(clock, reset):
    """
    """
    glbl = Global(clock, reset)
    csrbus = AXI4Lite(data_width=32, address_width=16)
    
    