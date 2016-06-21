
from __future__ import print_function, division

from argparse import Namespace
from random import randint

import myhdl
from myhdl import instance, delay, StopSimulation

from rhea import Clock, Reset, Global
from rhea.system import Wishbone

from rhea.cores.sdram import SDRAMInterface
from rhea.cores.sdram import sdram_sdr_controller
from rhea.models.sdram import SDRAMModel
from rhea.models.sdram import sdram_controller_model

from rhea.utils.test import run_testbench, tb_default_args


def test_sdram(args=None):
    """ SDRAM controller testbench
    """
    args = tb_default_args(args)

    # @todo: get the number of address to test from argparse
    num_addr = 100   # number of address to test
    
    # internal clock
    clock = Clock(0, frequency=50e6)
    reset = Reset(0, active=0, async=False)

    # sdram clock
    clock_sdram = Clock(0, frequency=100e6)

    # interfaces to the modules
    glbl = Global(clock=clock, reset=reset)
    ixbus = Wishbone(glbl=glbl, data_width=32, address_width=32)
    exbus = SDRAMInterface()
    exbus.clk = clock_sdram

    # Models
    sdram = SDRAMModel(exbus)   # model driven by model :)

    max_addr = 2048   # @todo: add actual SDRAM memory size limit
    max_data = 2**16  # @todo: add actual databus width

    @myhdl.block
    def bench_sdram():
        """
        This test exercises a SDRAM controller ...
        """

        tbmdl_sdm = sdram.process()
        tbmdl_ctl = sdram_controller_model(exbus, ixbus)

        # this test currently only exercises the models, 
        # insert a second SDRAMInterface to test an actual 
        # controller
        # tbdut = sdram_sdr_controller(ibus, exbus)
        tbclk = clock.gen(hticks=10*1000)
        tbclk_sdram = clock_sdram.gen(hticks=5*1000)

        @instance
        def tbstim():
            reset.next = reset.active
            yield delay(18000)
            reset.next = not reset.active

            # test a bunch of random addresses
            try:
                saved_addr_data = {}
                for ii in range(num_addr):
                    # get a random address and random data, save the address and data
                    addr = randint(0, max_addr-1)
                    data = randint(0, max_data-1)
                    saved_addr_data[addr] = data
                    yield ixbus.writetrans(addr, data)
                    yield ixbus.readtrans(addr)
                    read_data = ixbus.get_read_data()
                    assert read_data == data, "{:08X} != {:08X}".format(read_data, data)

                yield delay(20*1000)

                # verify all the addresses have the last written data
                for addr, data in saved_addr_data.items():
                    yield ixbus.readtrans(addr)
                    read_data = ixbus.get_read_data()
                    assert read_data == data
                    yield clock.posedge

                for ii in range(10):
                    yield delay(1000)

            except AssertionError as err:
                # if test check fails about let the simulation run more cycles,
                # useful for debug
                yield delay(20000)
                raise err

            raise StopSimulation

        return tbclk, tbclk_sdram, tbstim, tbmdl_sdm, tbmdl_ctl

    run_testbench(bench_sdram, timescale='1ps')


if __name__ == '__main__':
    test_sdram(Namespace())
