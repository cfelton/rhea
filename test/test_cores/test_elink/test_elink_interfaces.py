
from __future__ import print_function, division

from random import randint

import myhdl
from myhdl import (Signal, always, instance, delay, StopSimulation)

from rhea.cores.elink import ELink   # ELink interface
from rhea.cores.elink import EMesh   # EMesh interface
# a simple model of a device with an ELink interface
from rhea.models.elink import elink_asic_model
# a simple model for the FPGA side
from rhea.models.elink import elink_external_model
from rhea.utils.test import run_testbench, tb_args, tb_default_args


def test_elink_interfaces(args=None):
    """ test the ELink interface """
    args = tb_default_args(args)

    clock = Signal(bool(0))
    # create the interfaces
    elink = ELink()       # links the two components (models)
    emesh = EMesh(clock)  # interface into the Elink external component

    @myhdl.block
    def bench_elink_interface():
        tbnorth = elink_external_model(elink, emesh)
        tbsouth = elink_asic_model(elink)

        @always(delay(2500))
        def tbclk():
            clock.next = not clock

        @instance
        def tbstim():
            yield delay(1111)
            yield clock.posedge

            # send a bunch of write packets
            print("send packets")
            save_data = []
            yield emesh.write(0xDEEDA5A5, 0xDECAFBAD, 0xC0FFEE)
            save_data.append(0xDECAFBAD)
            for ii in range(10):
                addr = randint(0, 1024)
                data = randint(0, (2**32)-1)
                save_data.append(data)
                yield emesh.write(addr, data, ii)

            # the other device is a simple loopback, should receive
            # the same packets sent.
            while emesh.txwr_fifo.count > 0:
                print("  waiting ... {}".format(emesh))
                yield delay(8000)

            print("get packets looped back, ")
            while len(save_data) > 0:
                yield delay(8000)
                pkt = emesh.get_packet('wr')
                if pkt is not None:
                    assert pkt.data == save_data[0], \
                        "{} ... {:08X} != {:08X}".format(
                        pkt, int(pkt.data), save_data[0])
                    save_data.pop(0)

            for ii in range(27):
                yield clock.posedge

            raise StopSimulation

        return tbclk, tbnorth, tbsouth, tbstim

    run_testbench(bench_elink_interface, timescale='1ps', args=args)


if __name__ == '__main__':
    args = tb_args()
    test_elink_interfaces(args=args)
