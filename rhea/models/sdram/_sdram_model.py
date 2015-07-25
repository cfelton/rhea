
from __future__ import division
from __future__ import print_function

from math import ceil, floor

from myhdl import *


class SDRAMModel(object):
    """ SDRAM Model
    This will model the behavior and cycle accurate interface to
    an SDRAM device.

    Usage:
      extmembus = SDRAMInterface()          # interface and transactors
      sdram_model = SDRAMModel(extmembus)   # model
      sdram_proc = sdram_model.process()    # send to simulator

    This model implements the functionality described in the Micron
    datasheet for a 256Mb device.
    http://www.micron.com/parts/dram/sdram/mt48lc16m16a2b4-6a-it?pc=%7B5144650B-31FA-410A-993E-BADF981C54DD%7D

    Not convertible.
    """

    def __init__(self, intf):
        # external interface to the controller, the SDRAM interface
        # also contains the SDRAM timing parameters.
        self.intf = intf

        # emulate banks in an SDRAM
        self.banks = [{} for _ in range(intf.num_banks)]

        # typically DRAM is defined using states (@todo add reference)
        self.States = enum("IDLE", "ACTIVE")
        self.Commands = intf.Commands

    def process(self, skip_init=True):
        """
        @todo: documentation
        """
        intf = self.intf   # external SDRAM memory interface

        state = Signal(self.States.IDLE)
        cmd = Signal(self.Commands.NOP)

        @instance
        def mproc():
            cmd = self.Commands.NOP
            refresh_counter = 0

            # emulate the initialization sequence / requirement
            if skip_init:
                pass
            else:
                pass  # @todo: do init

            # the
            while True:
                # check the refresh counter
                if refresh_counter >= intf.cyc_ref:
                    # @todo: create specific
                    raise
                refresh_counter += 1

                if intf.cke:
                    cmd = intf.get_command()

                # synchronous RAM :)
                # @todo: if 'ddr' in intf.ver yield intf.clk.posedge, intf.clk.negedge
                yield intf.clk.posedge



        return mproc
