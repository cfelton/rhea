#
# Copyright (c) 2006-2013 Christopher L. Felton
#

from __future__ import division
from __future__ import print_function

from myhdl import *

from rhea.cores.fifo import fifo_ramp

from rhea.system import Clock
from rhea.system import Reset
from rhea.system import Global
from rhea.system import Wishbone
from rhea.system import FIFOBus

from rhea.utils.test import run_testbench


def test_fifo_ramp():

    clock = Clock(0, frequency=50e6)
    reset = Reset(0, active=1, async=False)
    glbl = Global(clock, reset)
    regbus = Wishbone(glbl)
    fifobus = FIFOBus()

    def _bench_fifo_ramp():
        tb_dut = fifo_ramp(clock, reset, regbus, fifobus,
                           base_address=0x0000)
        tb_rbor = regbus.m_per_outputs()
        tb_clk = clock.gen()
        
        asserr = Signal(bool(0))
                
        @instance 
        def tb_stim():
            try:
                yield delay(100)
                yield reset.pulse(111)

                # simply enable, enable the module and then
                # verify an incrementing pattern over the
                # fifobus
                yield regbus.write(0x00, 1)
                yield regbus.read(0x00)
                assert 1 == regbus.get_read_data(), "cfg reg write failed"

                # monitor the bus until ?? ramps
                Nramps, rr = 128, 0
                while rr < Nramps:
                    cnt = 0
                    for ii, sh in enumerate((24, 16, 8, 0,)):
                        yield regbus.read(0x08+ii)
                        cnt = cnt | (regbus.get_read_data() << sh)
                    rr = cnt

            except AssertionError as err:
                asserr.next = True
                for _ in range(10):
                    yield clock.posedge
                raise err

            raise StopSimulation

        # monitor the values from the fifo bus, it should
        # be a simple "ramp" increasing values
        _mask = 0xFF
        _cval = Signal(modbv(0, min=0, max=256))

        @always(clock.posedge)
        def tb_mon():
            if fifobus.wr:
                assert _cval == fifobus.wdata
                _cval.next = _cval+1

        return tb_clk, tb_dut, tb_stim, tb_mon, tb_rbor

    run_testbench(_bench_fifo_ramp)


if __name__ == '__main__':
    test_fifo_ramp()
