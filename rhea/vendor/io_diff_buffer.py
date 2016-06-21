
import myhdl
from myhdl import always_comb


@myhdl.block
def input_diff_buffer(in_p, in_n, sig):

    num_channels = len(sig)

    @always_comb
    def rtl_buffer_list():
        for ii in range(num_channels):
            sig[ii].next = in_p[ii] and not in_n[ii]

    @always_comb
    def rtl_buffer():
        sig.next = in_p and not in_n

    if isinstance(sig, list):
        gens = (rtl_buffer_list,)
    else:
        gens = (rtl_buffer,)

    return gens


@myhdl.block
def output_diff_buffer(sig, out_p, out_n):

    num_channels = len(sig)

    @always_comb
    def rtl_buffer_list():
        for ii in range(num_channels):
            out_p.next[ii] = sig[ii]
            out_n.next[ii] = not sig[ii]

    @always_comb
    def rtl_buffer():
        out_p.next = sig
        out_n.next = not sig

    if isinstance(sig, list):
        gens = (rtl_buffer_list,)
    else:
        gens = (rtl_buffer,)

    return gens
