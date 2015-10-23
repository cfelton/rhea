
from __future__ import absolute_import

from . import altera, xilinx, lattice


def device_pll(pll_intf):
    """ This module will generate the clocks  """

    if pll_intf.vendor == 'altera':
        device_inst = altera.device_pll(pll_intf)
    elif pll_intf.vendor == 'xilinx':
        device_inst = xilinx.device_pll(pll_intf)
    else:
        raise TypeError("Invalid vendor {}".format(pll_intf.vendor))
        
    return device_inst
