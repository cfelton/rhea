
from __future__ import print_function, division

from math import ceil, floor
import myhdl
from myhdl import Signal, intbv, enum, instance, always_comb

from rhea import Signals
from rhea.cores.sdram import SDRAMInterface


class SDRAMModel(object):
    def __init__(self, intf):
        """ SDRAM Model
        This will model the behavior and cycle accurate interface to
        an SDRAM device.

        Usage:
            extmembus = SDRAMInterface()          # interface and transactors
            sdram_model = SDRAMModel(extmembus)   # model
            sdram_proc = sdram_model.process()    # send to simulator

        This model implements the functionality described in the Micron
        datasheet for a 256Mb device:
        http://www.micron.com/parts/dram/sdram/mt48lc16m16a2b4-6a-it?pc=%7B5144650B-31FA-410A-993E-BADF981C54DD%7D

        Not convertible.
        """
        assert isinstance(intf, SDRAMInterface)

        # external interface to the controller, the SDRAM interface
        # also contains the SDRAM timing parameters.
        self.intf = intf

        # emulate banks in an SDRAM
        self.banks = [{} for _ in range(intf.num_banks)]

        # typically DRAM is defined using states (@todo add reference)
        self.States = enum("IDLE", "ACTIVE")
        self.Commands = intf.Commands

    @myhdl.block
    def process(self, skip_init=True):
        """
        @todo: documentation
        """
        intf = self.intf   # external SDRAM memory interface

        state = Signal(self.States.IDLE)
        cmdmn = Signal(self.Commands.NOP)

        Commands, States = self.Commands, self.States

        @instance
        def mproc():
            cmd = self.Commands.NOP
            refresh_counter = 0

            # emulate the initialization sequence / requirement
            if skip_init:
                pass  # don't do anything
            else:
                pass  # @todo: do init

            while True:
                # check the refresh counter
                if refresh_counter >= intf.cyc_ref:
                    # @todo: create specific exception for refresh error
                    raise ValueError
                refresh_counter += 1

                intf.dqi.next = None   # release the bi-dir bus (default)
                bs, addr = int(intf.bs), int(intf.addr)
                if intf.cke:
                    cmd = intf.get_command()

                    # @todo: need to add the device specific states
                    if cmd == Commands.NOP:
                        pass  # print("[SDRAM] nop commands")
                    elif cmd == Commands.ACT:
                        pass  # print("[SDRAM] ack commands")
                    elif cmd == Commands.WR:
                        # @todo look at the intf.dq bus and only get if valid
                        data = 0
                        if intf.dq is not None:
                            data = int(intf.dq)
                        assert intf.dq == intf.wdq
                        self.banks[bs][addr] = data
                    elif cmd == Commands.RD:
                        data = 0
                        if addr in self.banks[bs]:
                            data = self.banks[bs][addr]
                        intf.rdq.next = data
                        intf.dqi.next = data

                # this command, will always be one clock delayed
                cmdmn.next = cmd
                # synchronous RAM :)
                # @todo: if 'ddr' in intf.ver yield intf.clk.posedge, intf.clk.negedge
                yield intf.clk.posedge

        # in the model the following signals are not used in a generator.
        # The traceSignals will skip over these signals because it doesn't
        # think it is used.  Mirror the signals here so they are traced.
        cs, ras, cas, we = Signals(bool(0), 4)

        @always_comb
        def mon():
            cs.next = intf.cs
            ras.next = intf.ras
            cas.next = intf.cas
            we.next = intf.we

        return mproc, mon
