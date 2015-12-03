
from __future__ import absolute_import

from . import SERDESInterface
from . import altera, xilinx


def device_serdes_input(serdes):
    assert isinstance(serdes, SERDESInterface)

    if serdes.vendor == 'altera':
        device_inst = altera.devce_serdes_input(serdes)
    elif serdes.vendor == 'xilinx':
        device_inst = xilinx.device_serdes_input(serdes)

    return device_inst


def device_serdes_output(serdes):
    assert isinstance(serdes, SERDESInterface)

    if serdes.vendor == 'altera':
        device_inst = altera.devce_serdes_output(serdes)
    elif serdes.vendor == 'xilinx':
        device_inst = xilinx.device_serdes_output(serdes)

    return device_inst


def serdes_output_bank(serdes_intf_list):
    assert isinstance(serdes_intf_list, (list, tuple,))

    mods = []
    for intf in serdes_intf_list:
        g = device_serdes_output(intf)
        mods.append(g)

    return mods


def serdes_input_bank(serdes_intf_list):
    assert isinstance(serdes_intf_list, (list, tuple,))

    mods = []
    for intf in serdes_intf_list:
        g = device_serdes_input(intf)
        mods.append(g)

    return mods

