
from collections import OrderedDict
from myhdl import *
from ...system import RegisterFile,Register,RegisterBits

regdef = OrderedDict()

# -- a basic configuration register --
regcfg = Register('cfg',0x00,8,'rw',0)
regcfg.comment = "fifo ramp configuration register"
regcfg.add_bits('enable',slice(1,0),"enable fifo ramp")
regdef[regcfg.name] = regcfg

# -- division register 0 --
# 32-bit clock division register
for ii,regname in enumerate(('div3','div2','div1','div0')):
    regdiv = Register(regname,0x04+ii,8,'rw',0)
    regdiv.comment = "division register most significant byte"
    regdiv.add_bits('%sb'%(regname),slice(8,0),"rate control divisor")
    regdef[regdiv.name] = regdiv

# -- number of ramps completed --
# 32-bit 
for ii,regname in enumerate(('cnt3','cnt2','cnt1','cnt0')):
    regcnt = Register(regname,0x08+ii,8,'ro',0)
    regcnt.comment = "the number of ramp cycles completed"
    regcnt.add_bits('%sb'%(regname),slice(8,0),"count")
    regdef[regcnt.name] = regcnt
                           
regfile = RegisterFile(regdef)
