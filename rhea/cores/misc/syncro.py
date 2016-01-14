

from myhdl import Signal, intbv, always, always_comb


def syncro(clock, sigin, sigout, num_sync_ff=2):
    """ signal synchronizer
    Typically
    :param sigin:
    :param sigout:
    :param num_sync_ff:
    :return:
    """
    assert type(sigin.val) == type(sigout.val)
    assert len(sigin) == len(sigout)
    sigtype = sigin.val
    staps = [Signal(sigtype) for _ in range(num_sync_ff)]

    @always(clock.posedge)
    def rtl():
        staps[0].next = sigin
        for ii in range(1, num_sync_ff):
            staps[ii].next = staps[ii-1]

    @always_comb
    def rtl_assign():
        sigout.next = staps[num_sync_ff-1]

    return rtl, rtl_assign
