# Copyright (c) 2014-2015 Christopher Felton


from __future__ import division
from __future__ import print_function


# import all the board definitions
from .xilinx import (Anvyl, Atlys, Mojo, Nexys, NexysVideo, Parallella,
                     PapilioOne, PapilioPro, SX1, UFO400, Waxwing45,
                     Waxwing45carrier, Xula, Xula2, Xula2StickItMB,
                     XUPV2P, Zybo, CModA7_15T, CModA7_35T)
from .altera import (DE0Nano, DE0NanoSOC, DE0CV, DE1SOC)
from .lattice import (Icestick, CATBoard)


xbrd = {'anvyl': Anvyl, 'atlys': Atlys, 'mojo': Mojo, 'nexys': Nexys,
        'nexys_video': NexysVideo, 'parallella': Parallella,
        'pone': PapilioOne, 'ppro': PapilioPro, 'sx1': SX1,
        'ufo400': UFO400, 'waxwing45': Waxwing45,
        'waxwing45carrier': Waxwing45carrier, 'xula': Xula,
        'xula2': Xula2, 'xula2_stickit_mb': Xula2StickItMB,
        'xupv2p': XUPV2P, 'zybo': Zybo, 'cmoda7_15t': CModA7_15T,
        'cmoda7_35t': CModA7_35T,
        }

abrd = {'de0nano': DE0Nano, 'de0nano_soc': DE0NanoSOC, 'de0cv': DE0CV, 
        'de1_soc': DE1SOC,}

lbrd = {'icestick': Icestick, 'catboard': CATBoard}


def get_board(name):
    """ retrieve a board definition from the name provided.
    """
    brd = None
    if name in xbrd:
        brd = xbrd[name]()
    elif name in abrd:
        brd = abrd[name]()
    elif name in lbrd:
        brd = lbrd[name]()
    else:
        # @todo: print out a list of boards and descriptions
        raise ValueError("Invalid board %s"%(name,))

    return brd


def get_all_board_names():
    return list(xbrd.keys()) + list(abrd.keys()) + list(lbrd.keys())
