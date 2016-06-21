
from __future__ import absolute_import

"""
Psuedo random bit sequence (PRBS)
"""

from random import randint
import myhdl
from myhdl import Signal, intbv, always_seq, always_comb, bin, now
from .prbs_table import prbs_feedback_taps


def get_feedback_taps(order, feedback_taps):
    # if the feedback taps were not supplied, grab the first
    # set from the table
    if feedback_taps is None:
        if order in prbs_feedback_taps:
            feedback_taps = prbs_feedback_taps[order][0]
        else:
            raise Exception("No feedback taps defined for order {}".format(order))
            
    # create a bitmap (bit-vector) for the feedback taps 
    taps_bitmap = "".join(['1' if ii in feedback_taps else '0' for ii in range(order)])
    taps_const = int(intbv(taps_bitmap[::-1])[order:])
    taps = Signal(intbv(taps_const)[order:])
    
    return taps_const, taps 
    

@myhdl.block
def lfsr_feedback(lfsr, lfsrfb, prbscm, taps_const):
    """ determine the feedback logic for the LFSR 
    """
    nbits, z = len(lfsr), len(lfsr)-1 
    assert len(lfsr) == len(lfsrfb)
    wbits = len(prbscm)
    
    @always_comb
    def beh():
        f = intbv(0)[nbits:]
        d = intbv(0)[nbits:]
        p = intbv(0)[wbits:] 
        taps = intbv(taps_const)[nbits:]
        f[:] = lfsr
        for w in range(0, wbits):
            p[w] = f[0]
            d[z] = f[0]
            for ii in range(nbits-1):
                if taps[ii+1] == 1:
                    d[ii] = f[ii+1] ^ f[0]
                else:
                    d[ii] = f[ii+1]
            f[:] = d
            
        lfsrfb.next = f 
        prbscm.next = p 
        
    return beh
    
@myhdl.block
def prbs_generate(glbl, prbs, enable=None, inject_error=None,
                  order=4, feedback_taps=None, initval=None):
    """ Galois (one-to-many) LFSR PRBS generater


    Ports:
      glbl: clock and reset in Global interface
      prbs: prbs output

    Parameters:
      feedback_taps: feedback taps for the LFSR
      initval: LFSR initial value
    """

    nbits, z = order, order-1
    wlen = len(prbs)

    # get the taps bitmap, which taps are used for feedback 
    taps_const, taps = get_feedback_taps(order, feedback_taps)
    
    clock, reset = glbl.clock, glbl.reset
    initval = randint(1, 2**nbits-1) if initval is None else initval
    lfsr = Signal(intbv(initval)[nbits:])

    if enable is None:
        enable = True

    if inject_error is None:
        inject_error = False

    lfsrfb = Signal(intbv(0)[nbits:])
    prbscm = Signal(prbs.val)

    # the LFSR feedback logic
    lfsr_inst = lfsr_feedback(lfsr, lfsrfb, prbscm, taps_const)

    @always_seq(clock.posedge, reset=reset)
    def beh_lfsr():
        if enable:
            lfsr.next = lfsrfb
            prbs.next = prbscm ^ 1 if inject_error else prbscm
        else:
            lfsr.next = initval
            prbs.next = 0

        # constant bit-vector, set during reset also force here 
        # in case the system doesn't have a reset 
        taps.next = taps_const

    return lfsr_inst, beh_lfsr


@myhdl.block
def prbs_check(glbl, prbs, locked, word_count, error_count,
               order=4, feedback_taps=None):
    """ 
    
    """
    nbits, wbits = order, len(prbs)
    
    # get the taps bitmap, which taps are used for feedback 
    taps_const, taps = get_feedback_taps(order, feedback_taps)
    
    # number arbitrary chosen, the break lock count should be
    # much greater than the lock, the break lock should account
    # for the maximum burst errors ... 
    locked_count = 17
    break_count = 213 
    
    clock, reset = glbl.clock, glbl.reset
    count = Signal(intbv(0, min=0, 
                         max=max(locked_count, break_count)+1))

    lfsr = Signal(intbv('1'*nbits)[nbits:])
    lfsrfb = Signal(intbv(0)[nbits:])
    prbscm = Signal(prbs.val)
    
    # the LFSR feedback logic 
    lfsr_inst = lfsr_feedback(lfsr, lfsrfb, prbscm, taps_const)
    
    @always_seq(clock.posedge, reset=reset)
    def beh():
        # default cause, load the next value 
        lfsr.next = lfsrfb 
        
        # determine counters to increment based on the state 
        if locked:
            # @todo: only increment word_count and error_count if the max 
            # @todo: has not been reached
            word_count.next = word_count + 1 

            if count >= break_count:
                locked.next = False
                count.next = 0
                # @todo: ?? clear error count ??
            elif prbs != prbscm:
                # @todo: count the number of bit errors 
                error_count.next = error_count + 1
                count.next = count + 1 
            else:
                count.next = 0

        elif count > 0:        
            if prbs == prbscm:
                count.next = count + 1 
            else:
                count.next = 0
                
            if count >= locked_count:
                locked.next = True 
                
        else:
            # @todo: need to decode prbs to lfsr state if wbits >= nbits 
            # @todo: or accumulate enough prbs bits and then determine 
            # @todo: prbs state 
            if prbs == prbscm:
                count.next = 1
            else:
                lfsr.next = lfsr 
                count.next = 0
                
    return lfsr_inst, beh 

