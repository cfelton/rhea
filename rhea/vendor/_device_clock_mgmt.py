
from __future__ import absolute_import

from . import altera, xilinx


def device_clock_mgmt(clkmgmt):
    """ This module will generate the clocks  """

    if clkmgmt.vendor == 'altera':
        device_inst = altera.device_clock_mgmt(clkmgmt)
    elif clkmgmt.vendor == 'xilinx':
        device_inst = xilinx.device_clock_mgmt(clkmgmt)
    else:
        raise TypeError("Invalid vendor {}".format(clkmgmt.vendor))

    return device_inst
