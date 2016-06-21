
import myhdl
from myhdl import always_comb


@myhdl.block
def input_diff_buffer(inp, inn, sig):

    num_channels = len(sig)

    if isinstance(sig, list):

        @always_comb
        def rtl_buffer_list():
            for ii in range(num_channels):
                sig[ii].next = inp[ii] and not inn[ii]

        gens = (rtl_buffer_list,)

    else:

        @always_comb
        def rtl_buffer():
            sig.next = inp and not inn

        gens = (rtl_buffer,)

    return gens


@myhdl.block
def output_diff_buffer(sig, outp, outn):

    num_channels = len(sig)

    if isinstance(sig, list):

        @always_comb
        def rtl_buffer_list():
            for ii in range(num_channels):
                outp.next[ii] = sig[ii]
                outn.next[ii] = not sig[ii]

        gens = (rtl_buffer_list,)

    else:
        
        @always_comb
        def rtl_buffer():
            outp.next = sig
            outn.next = not sig

        gens = (rtl_buffer,)

    return gens
