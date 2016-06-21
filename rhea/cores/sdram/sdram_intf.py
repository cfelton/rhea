
from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

from math import ceil, floor

from myhdl import Signal, TristateSignal, intbv, enum


class SDRAMInterface(object):
    clock_frequency = 100e6
    timing = {  # all timing parameters in ns
        'init': 200000.0,   # min init interval
        'ras': 45.0,        # min interval between active precharge commands
        'rcd': 20.0,        # min interval between active R/W commands
        'ref': 64000000.0,  # max refresh interval
        'rfc': 65.0,        # refresh operaiton duration
        'rp': 20.0,         # min precharge command duration
        'xsr': 75.0,        # exit self-refresh time
        'wr': 55.0,         # @todo ...
    }

    addr_width = 12   # SDRAM address width
    data_width = 16   # SDRAM data width

    def __init__(self, num_banks=4, addr_width=12, data_width=16, ver='sdr'):

        # signals in the interface
        self.frequency = 0.            # @todo:
        self.clk = Signal(bool(0))     # interface clock
        self.cke = Signal(bool(0))     # clock enable
        self.cs = Signal(bool(0))      # chip select
        self.cas = Signal(bool(0))     # column address strobe
        self.ras = Signal(bool(0))     # row address strobe
        self.we = Signal(bool(0))      # write strobe
        self.bs = Signal(intbv(0)[2:]) # bank select
        self.addr = Signal(intbv(0)[addr_width:])
        self.dqm = Signal(bool(0))
        self.dqml = Signal(bool(0))
        self.dqmh = Signal(bool(0))
        self.dq = TristateSignal(intbv(0)[data_width:])
        # the controller and SDRAM bi-dir bus drivers
        self.dqo = self.dq.driver()
        self.dqi = self.dq.driver()

        # the following separate write and read buses are
        # not used in an actual device.  They are used by
        # the model for debug and testing.
        self.wdq = Signal(intbv(0)[data_width:])
        self.rdq = Signal(intbv(0)[data_width:])

        # configurations for the SDRAM interfacing with
        self.num_banks = num_banks
        self.addr_width = addr_width
        self.data_width = data_width
        self.ver = ver

        # saved read, transactors save the read data here
        self.read_data = None

        # generic commands for a DRAM, override these for specific (S)DRAM devices
        # @todo: attribute of the interface or global definition?
        self.Commands = enum(
            "NOP",  # no operation, ignore all inputs
            "ACT",  # activate a row in a particular bank
            "RD",   # read, initiate a read burst to an active row
            "WR",   # write, initial a write burst to an active row
            "PRE",  # precharge, close a row in a particular bank
            "REF",  # refresh, start a refresh operation
            # extended commands (???)
            "LMR",  # load mode register
            )

        # extract the default timing parameters, all parameters in ns
        # but convert to "ps" like ticks.
        cycles = {}
        for k, v in self.timing.items():
            cycles[k] = (v * (self.clock_frequency / 1e9))
            # @todo: if 'ddr' in self.ver: cycles[k] *= 2

        # add the cycle numbers to the
        for k, v in cycles.items():
            # majority of the timing parameters are maximum times,
            # floor error on the side of margin ...
            self.__dict__['cyc_'+k] = int(floor(v))

        # convert the time parameters to simulation ticks
        # @todo: where to get the global simulation step?
        for k, v in self.timing.items():
            self.__dict__['tick_'+k] = int(ceil(v * 1000))

    def get_data_driver(self, dir='o'):
        if dir == 'o':
            drv = self.dqo
        else:
            drv = self.dqi
        return drv

    def get_command(self):
        """ extract the current command from based in the interface signals
        Command table
          cs  ras  cas  we  dqm
          H   X    X    X   X    : NOP  (command inhibit)
          L   H    H    H   X    : NOP
          L   H    H    L   X    :      (burst term)
          L   H    L    H   X    : RD
          L   H    L    L   X    : WR
          L   L    H    H   X    : ACT
          L   L    H    L   X    : PRE
          L   L    L    H   X    : REF  (auto refresh)
          L   L    L    L   X    : LRM  (load mode register)
        :return:
        """
        cs, ras, cas, we, dqm = (self.cs, self.ras, self.cas,
                                 self.we, self.dqm)
        cmd = self.Commands.NOP
        if not cs:
            if ras and not cas and we:
                cmd = self.Commands.RD
            elif ras and not cas and not we:
                cmd = self.Commands.WR
            elif not ras and cas and we:
                cmd = self.Commands.ACT
            elif not ras and cas and not we:
                cmd = self.Commands.PRE
            elif not ras and not cas and we:
                cmd = self.Commands.REF
            elif not ras and not cas and not we:
                cmd = self.Commands.LRM
        return cmd

    def _set_cmd(self, cmd):
        pass

    def _nop(self):
        self.cs.next = False
        self.ras.next = True
        self.cas.next = True
        self.we.next = True
        yield self.clk.posedge

    def _activate(self, row_addr):
        self.addr.next = row_addr
        self.cs.next = False
        self.ras.next = False
        self.cas.next = True
        self.we.next = True
        yield self.clk.posedge

    def _write(self, addr, val):
        self.addr.next = addr
        self.wdq.next = val     # transaction bus only
        self.dqo.next = val     # host side driver (controller)
        self.cs.next = False
        self.ras.next = True
        self.cas.next = False
        self.we.next = False
        yield self.clk.posedge
        self.dqo.next = None

    def _read(self, addr):
        self.addr.next = addr
        self.cs.next = False
        self.ras.next = True
        self.cas.next = False
        self.we.next = True
        yield self.clk.posedge
        if self.dq is not None and self.dqo is None:
            self.rdq.next = self.dq

    def write(self, val, row_addr, col_addr, bankid=0, burst=1):
        """ Controller side write
        This is a transaction generator, this generator is used to
        emulate a host write to an SDRAM device.

        @todo: complete burst transaction
        Not convertible.
        """
        # start on the posedge of the interface clock
        yield self.clk.posedge
        self.bs.next = bankid
        self.cke.next = True
        yield self._nop()
        yield self._activate(row_addr)
        yield self._nop()
        yield self._write(col_addr, val)
        yield self._nop()
        self.cke.next = False

    def read(self, row_addr, col_addr, bankid=0, burst=1):
        """ Controller side read
        This is a transaction generator, this generator is used to
        emulate a host read to an SDRAM device.

        @todo: complete burst transaction
        Not convertible.
        """
        # start of the posedge of the interface clock
        yield self.clk.posedge
        self.bs.next = bankid
        self.cke.next = True
        yield self._nop()
        yield self._activate(row_addr)
        yield self._nop()
        yield self._read(col_addr)
        yield self._nop()
        self.cke.next = False
        self.read_data = int(self.rdq)

    def get_read_data(self):
        return self.read_data
