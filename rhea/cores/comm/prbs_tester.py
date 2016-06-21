
from __future__ import absolute_import

import myhdl
from myhdl import Signal, intbv

from rhea.system import ControlStatus
from . import prbs_generate
from . import prbs_check


class PRBSControlStatus(ControlStatus):
    # global control signals
    enable = Signal(bool(0))

    # generator control signals
    inject_error = Signal(bool(0))

    # checker control signals
    clear_count = Signal(bool(0))

    # checker status signals
    locked = Signal(bool(0))
    locked.driven = True
    word_count = Signal(intbv(0)[64:])
    word_count.driven = True
    error_count = Signal(intbv(0)[64:])
    error_count.driven = True


@myhdl.block
def prbs_tester(glbl, prbso, prbsi, memmap, order=23):
    """PRBS tester, generator and checker

    Arguments:
      glbl: global signals, clock, reset, enable, etc.
      prbso: PRBS output
      prbsi: PRBS input
      memmap: memory-mapped interface

    Parameters:
      order: PRBS order, prbs length = 2**order-1
    """

    # create the control and status signals and the logic to
    # interface to the memory-mapped bus.
    csr = PRBSControlStatus()
    csr_inst = memmap.add_csr(csr)

    # instantiate the generate and check modules
    gen_inst = prbs_generate(glbl, prbso, csr.enable, csr.inject_error,
                             order=order)

    chk_inst = prbs_check(glbl, prbsi, csr.locked, csr.word_count,
                          csr.error_count, order=order)

    return csr_inst, gen_inst, chk_inst








