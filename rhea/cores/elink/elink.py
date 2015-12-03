
from __future__ import division
from __future__ import print_function


def elink_module(elink_intf, emesh_intf):
    """ The Adapteva ELink off-chip communication channel.
    
    Interfaces:
      elink_intf: The external link signals
      emesh_intf: The internal EMesh packet interface

    """

    # keep track of all the myhdl generators
    mod_inst = []

    # clock and reset config
    # g = ecfg_elink()
    # mod_inst.append(g)

    # receiver
    # g = erx(elink, emesh_e)
    # mod_inst.append(g)

    # transmitter
    # g = etx(elink, emesh_e)
    # mod_inst.append(g)

    # CDC FIFO
    # g = ecfg_fifo(emesh, emesh_e)
    # mod_inst.append(g)

    # Vendor specific IO SERDES
    # g = io_serdes()
    # mod_inst.append(g)

    return mod_inst
