
import myhdl
from myhdl import Signal, always_comb


@myhdl.block
def device_input_diff_buffer(in_p, in_n, sig):
    """

    :param in_p: bit-vector
    :param in_n: bit-vector
    :param sig: list-of-signal bools
    :return:
    """

    if isinstance(sig, list):
        num_channels = len(sig)

        @always_comb
        def rtl_buffer():
            for ii in range(num_channels):
                sig[ii].next = in_p[ii] and not in_n[ii]

    else:

        @always_comb
        def rtl_buffer():
            sig.next = in_p and not in_n

    return rtl_buffer
