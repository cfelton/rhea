
import myhdl
from myhdl import Signal, intbv, always, always_comb


@myhdl.block
def syncro(clock, sigin, sigout, posedge=None, negedge=None,
           num_sync_ff=3):
    """ signal synchronizer

    Arguments:
      sigin: signal input.
      sigout: synchronized signal output.
      posedge: a positive edge in the sync
      negedge: a negitive edge in the sync

    Parameters:
      num_sync_ff: the number of sync stages.

    """
    assert type(sigin.val) == type(sigout.val)
    assert len(sigin) == len(sigout)
    sigtype = sigin.val
    staps = [Signal(sigtype) for _ in range(num_sync_ff)]

    @always(clock.posedge)
    def beh_sync_stages():
        staps[0].next = sigin
        for ii in range(1, num_sync_ff):
            staps[ii].next = staps[ii-1]

    @always_comb
    def beh_assign():
        sigout.next = staps[num_sync_ff-1]

    nsf = num_sync_ff
    if posedge is not None:
        @always_comb
        def beh_posedge():
            posedge.next = not staps[nsf-1] and staps[nsf-2]

    if negedge is not None:
        @always_comb
        def beh_negedge():
            negedge.next = staps[nsf-1] and not staps[nsf-2]

    return myhdl.instances()
