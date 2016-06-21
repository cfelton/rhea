
from __future__ import absolute_import

import myhdl
from .._device_serdes_prim import device_serdes_input_prim
from .._device_serdes_prim import device_serdes_output_prim


@myhdl.block
def device_serdes_input(serdes):

    prim_inst = device_serdes_input_prim(serdes)

    return prim_inst


@myhdl.block
def device_serdes_output(serdes):

    prim_inst = device_serdes_output_prim(serdes)

    return prim_inst
