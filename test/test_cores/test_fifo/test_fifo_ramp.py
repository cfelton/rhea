#
# Copyright (c) 2006-2013 Christopher L. Felton
#

from __future__ import print_function, division

from argparse import Namespace

import myhdl
from myhdl import Signal, modbv, always
from myhdl import instance, delay, now, StopSimulation

from rhea.cores.fifo import fifo_ramp

from rhea.system import Global, Clock, Reset
from rhea.system import Wishbone
from rhea.system import FIFOBus

from rhea.utils.test import run_testbench, tb_args, tb_default_args
from rhea.utils.test import skip_long_sim_test


@skip_long_sim_test
def test_fifo_ramp(args=None):
    args = tb_default_args(args)
    clock = Clock(0, frequency=50e6)
    reset = Reset(0, active=1, async=False)
    glbl = Global(clock, reset)
    regbus = Wishbone(glbl)
    fifobus = FIFOBus()

    @myhdl.block
    def bench_fifo_ramp():
        tbdut = fifo_ramp(glbl, regbus, fifobus, base_address=0x0000)
        tbrbor = regbus.interconnect()
        tbclk = clock.gen()
        
        asserr = Signal(bool(0))
                
        @instance 
        def tbstim():
            print("start fifo ramp test")
            try:
                yield delay(100)
                yield reset.pulse(111)

                # verify an incrementing pattern over the fifobus
                yield regbus.writetrans(0x07, 2)  # div of two
                yield regbus.readtrans(0x07)
                assert 2 == regbus.get_read_data()

                yield regbus.writetrans(0x00, 1)  # enable
                yield regbus.readtrans(0x00)
                assert 1 == regbus.get_read_data(), "cfg reg write failed"

                # monitor the bus until ?? ramps
                Nramps, rr, timeout = 128, 0, 0
                while rr < Nramps and timeout < (20*Nramps):
                    cnt = 0
                    for ii, sh in enumerate((24, 16, 8, 0,)):
                        yield delay(1000)
                        yield regbus.readtrans(0x08+ii)
                        cntpart = regbus.get_read_data()
                        cnt = cnt | (cntpart << sh)
                        print("{:<8d}: ramp count[{:<4d}, {:d}]: {:08X}, {:02X} - timeout {:d}".format(
                               now(), rr, ii, cnt, cntpart, timeout))
                    timeout += 1
                    # @todo: add ramp check
                    if cnt != rr or (timeout % 1000) == 0:
                        print("   ramp {}  {}".format(int(cnt), int(rr),))
                    rr = int(cnt)
                print("{}, {}, {}".format(Nramps, rr, timeout))
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
        def tbmon():
            if fifobus.write:
                assert _cval == fifobus.write_data
                _cval.next = _cval+1

        return tbclk, tbdut, tbstim, tbmon, tbrbor

    run_testbench(bench_fifo_ramp, args=args)


if __name__ == '__main__':
    test_fifo_ramp(tb_args())
