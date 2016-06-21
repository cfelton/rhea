
from __future__ import division, print_function


def elink_module(elink_intf, emesh_intf):
    """ The Adapteva ELink off-chip communication channel.
    
    Interfaces:
      elink_intf: The external link signals
      emesh_intf: The internal EMesh packet interface

    """

    # keep track of all the myhdl instances
    mod_inst = []

    # clock and reset config
    # mod_inst += ecfg_elink()

    # receiver
    # mod_inst += erx(elink, emesh_e)

    # transmitter
    # mod_inst += etx(elink, emesh_e)

    # CDC FIFO
    # mod_inst += ecfg_fifo(emesh, emesh_e)

    # Vendor specific IO SERDES
    # mod_inst += io_serdes()

    return mod_inst
