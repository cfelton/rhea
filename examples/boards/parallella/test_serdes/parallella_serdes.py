
from __future__ import print_function
from __future__ import division

import argparse

from myhdl import Signal, intbv

from rhea.system import Global, Clock, Reset
from rhea.cores.misc import io_stub
from rhea.cores.comm import prbs_generate
from rhea.cores.comm import prbs_check

from rhea.build import get_board


def parallella_serdes(clock, reset,
                      # serial_tx_p, serial_tx_n,
                      # serial_rx_p, serial_rx_n,
                      sdi, sdo
         ):
    nbanks = 4
    # nbanks = len(serial_tx_p)
    # assert (len(serial_tx_p) == len(serial_tx_n) ==
    #         len(serial_rx_p) == len(serial_rx_n) )

    glbl = Global(clock, reset)
    # @todo: this is temporary for synthesis testing
    pin = [Signal(intbv(0)[8:]) for _ in range(nbanks)]
    pout = [Signal(intbv(0)[8:]) for _ in range(nbanks)]

    io_inst = io_stub(clock, reset, sdi, sdo, pin, pout)

    locked = [Signal(bool(0)) for _ in range(nbanks)]
    word_count = [Signal(intbv(0)[64:])]
    error_count = [Signal(intbv(0)[64:])]
    prbs_insts = []
    for bank in range(nbanks):
        gg = prbs_generate(glbl, pout[bank], order=23)
        gc = prbs_check(glbl, pin[bank], locked[bank],
                        word_count[bank], error_count[bank], order=23)
        prbs_insts.append(gg)
        prbs_insts.append(gc)

    return io_inst, prbs_insts


def build(args):
    # @todo: use parallella board, use an ISE support board for now ...
    brd = get_board('atlys')
    # @todo: temporary for existing board
    brd.add_port_name('sdi', 'uart_rxd')
    brd.add_port_name('sdo', 'uart_txd')

    flow = brd.get_flow(parallella_serdes)
    flow.run()
    info = flow.get_utilization()


def cliparse():
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    return args


def main():
    args = cliparse()
    build(args)


if __name__ == '__main__':
    main()
