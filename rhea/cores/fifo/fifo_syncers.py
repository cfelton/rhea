#
# Copyright (c) 2006-2014 Christopher L. Felton
#

import myhdl
from myhdl import Signal, intbv, always_seq


@myhdl.block
def sync_reset(clock, reset_in, reset_out, sync_length=2):
    """ Synchronize a reset
    Use a register chain to synchronize a reset, the registers are 
    reset asynchronously and the output reset will be released 
    synchronously.

    Arguments:
        clock: system clock
        reset_in: external reset to be sync'd
        reset_out: sync'd reset
    Parameters:
        sync_length: required length of the sync
    """
    reset_sync = [Signal(bool(reset_in.active)) for _ in range(sync_length)]

    @always_seq(clock.posedge, reset=reset_in)
    def beh():
        reset_sync[0].next = reset_in
        for i in range(0,sync_length-1):        
            reset_sync[i+1].next = reset_sync[i]
        reset_out.next = reset_sync[sync_length-1]

    return beh


@myhdl.block
def sync_mbits(clock, reset, signal_in, signal_out):
    """Two stage synchronizer
    """
    d1 = Signal(intbv(0)[len(signal_out):])

    @always_seq(clock.posedge, reset=reset)
    def beh():
        d1.next = signal_in
        signal_out.next = d1

    return beh
