
from __future__ import print_function
from __future__ import division

import myhdl
from myhdl import (Signal, ResetSignal, intbv, instance,
                   always, always_seq)

from rhea.system import Clock
from rhea.system import ticks_per_ns

from rhea.vendor import ClockManagement
from rhea.vendor import device_clock_mgmt

from rhea.vendor import SERDESInterface
from rhea.vendor import device_serdes_output
from rhea.vendor import device_serdes_input


def top_serdes_wrap(clockext, resetext,
                    sero_p, sero_n, seri_p, seri_n,
                    args=None):
    """
    """
    clkmgmt = ClockManagement(clockext, reset=resetext,
                              output_frequencies=(125e6, 1e9))
    clkmgmt.vendor = args.vendor

    # @todo: add external_reset_sync module