
from __future__ import absolute_import

"""
Psuedo random bit sequency (PRBS)
"""
from random import randint
from myhdl import Signal, intbv, always_seq, bin, now
from ._prbs_table import prbs_feedback_taps


def prbs_generate(glbl, prbs, order=4, feedback_taps=(0, 1), initval=None):
    """ Galois (one-to-many) LFSR PRBS generater


    Ports:
      glbl: clock and reset in Global interface
      prbs: prbs output

    Parameters:
      feedback_taps: feedback taps for the LFSR
      initval: LFSR initial value
    """

    nbits = order+1
    wlen = len(prbs)

    # if the feedback taps were not supplied, grab the first
    # set from the table
    if feedback_taps is None and order in prbs_feedback_taps:
        feedback_taps = prbs_feedback_taps[order][0]
    taps = tuple([1 if ii in feedback_taps else 0 for ii in range(nbits)])

    clock, reset = glbl.clock, glbl.reset
    initval = randint(1, 2**nbits-1) if initval is None else initval
    lfsr = Signal(intbv(initval)[nbits:])
    d, f = intbv(0)[nbits:], intbv(0)[nbits:]
    p = intbv(0)[wlen:]
    print("TAPS {}".format(taps))

    @always_seq(clock.posedge, reset=reset)
    def hdl_lfsr():
        f[:] = lfsr
        for w in range(wlen):
            p[w] = f[nbits-1]
            d[0] = f[nbits-1]
            for ii in range(1, nbits):
                # print("    [{:5d},{:5d}]: {}".format(w, ii, bin(d, nbits)))
                if taps[ii-1] == 1:
                    d[ii] = f[ii-1] ^ f[nbits-1]
                else:
                    d[ii] = f[ii-1]
            f[:] = d
        # print("{:12d}:   lfsr -> {}".format(now(), bin(d, nbits)))
        lfsr.next = d
        prbs.next = p

    return hdl_lfsr


def prbs_check(glbl, prbs, locked, word_count, error_count,
               order=4, feedback_taps=None):
    """ """
    pass
