
from __future__ import absolute_import

import myhdl
from . import altera, xilinx


@myhdl.block
def device_clock_mgmt(clkmgmt):
    """ This module will generate the clocks  """

    if clkmgmt.vendor == 'altera':
        device_inst = altera.device_clock_mgmt(clkmgmt)
    elif clkmgmt.vendor == 'xilinx':
        device_inst = xilinx.device_clock_mgmt(clkmgmt)
    else:
        # @todo: use a generic synthesizable description that may
        # @todo: or may not infer the primitive
        raise TypeError("Invalid vendor {}".format(clkmgmt.vendor))

    return device_inst
