# Copyright (c) 2014-2015 Christopher Felton


from __future__ import division
from __future__ import print_function


# import all the board definitions
from .xilinx import (Xula, Xula2, Xula2StickItMB, 
                     Pone, Anvyl, Mojo, Nexys, Atlys,
                     Zybo, Parallella, SX1, UFO400, XUPV2P)
from .altera import (DE0Nano, DE0NanoSOC, DE0CV)
from .lattice import (Icestick, CATBoard)


xbrd = {'xula': Xula, 'xula2': Xula2, 'xula2_stickit_mb': Xula2StickItMB,
        'pone': Pone, 'anvyl': Anvyl,
        'mojo': Mojo, 'atlys': Atlys, 'nexys': Nexys, 'zybo': Zybo,
        'parallella': Parallella, 'sx1': SX1, 'ufo400': UFO400,
        'xupv2p': XUPV2P,}

abrd = {'de0nano': DE0Nano, 'de0nano_soc': DE0NanoSOC, 'de0cv': DE0CV,}

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
