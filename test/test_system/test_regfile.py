#
# Copyright (c) 2006-2013 Christopher L. Felton
#

from random import randint
import traceback

import myhdl
from myhdl import Signal, ResetSignal, intbv, modbv, always, always_comb
from myhdl import instance, delay, StopSimulation

from rhea import Clock, Reset, Global
from rhea.system import Register, RegisterFile
from rhea.system import Wishbone
from rhea.utils.test import (run_testbench, tb_default_args,
                             tb_convert, tb_args,)

# only one register-file under test at a time, allow the generated
# register-file to be accessible from the testbench
regfile = None


def _create_mask(n):
    m = 1
    for _ in range(n):
        m = (m << 1) | 1
    return m


def create_regfile():
    """
    [0] 0x0018: control register
    [1] 0x0020:
    [2] 0x0040:
    [3] 0x0080:
    [4] 0x0100: regro (read-only)
    [5] 0x0200: status (read-only, with namedbits)
    :return:
    """
    global regdef
    print("creating test register file")
    regfile = RegisterFile()
    regfile.base_address = 0

    # --register 0--
    reg = Register('control', width=8, access='rw', default=0, addr=0x0018)
    reg.comment = "register 0"
    reg.add_namedbits('enable', slice(1, 0))  # read-only namedbit
    reg.add_namedbits('loop', slice(2, 1))    # read-only namedbit
    regfile.add_register(reg)
    
    # -- more registers register --
    for addr, default in zip((0x20, 0x40, 0x80),
                             (0xDE, 0xCA, 0xFB)):
        reg = Register('reg%s' % (addr,), 8, 'rw', default, addr)
        regfile.add_register(reg)

    # -- read only register --
    reg = Register('regro', 8, 'ro', 0xAA, 0x100)
    regfile.add_register(reg)

    # another read only register, with named bits
    reg = Register('status', 8, 'ro', 0, 0x200)
    reg.add_namedbits('error', slice(1, 0))  # bit 0, read-write namedbit
    reg.add_namedbits('ok', slice(2, 1))     # bit 1, read-write namedbit
    reg.add_namedbits('cnt', slice(8, 2))    # bits 7-2, read-write namedbit
    regfile.add_register(reg)

    return regfile


@myhdl.block
def peripheral_top(clock, reset, mon):
    glbl = Global(clock, reset)
    wb = Wishbone(glbl)
    inst = memmap_peripheral(glbl, wb, mon)
    return inst


@myhdl.block
def memmap_peripheral(glbl, regbus, mon):
    global regfile
    regfile = create_regfile()
    regfile_inst = regbus.add(regfile, name='test1')

    return regfile_inst


@myhdl.block
def memmap_peripheral_bits(glbl, regbus, mon):
    global regfile

    clock, reset = glbl.clock, glbl.reset
    regfile = create_regfile()
    regfile_inst = regbus.add(regfile, name='test2')
    count = modbv(0, min=0, max=1)

    @always(clock.posedge)
    def beh_roregs():
        count[:] = count + 1
        
        # only 'ro' registers can have named bits that can
        #   be set
        if count:
            regfile.error.next = True
            regfile.ok.next = False
        else:
            regfile.error.next = False
            regfile.ok.next = True
            
        if regfile.regro.rd:
            regfile.regro.next = mon

        regfile.cnt.next = count[5:]
        
    return regfile_inst, beh_roregs


def test_register_def():
    regfile = create_regfile()
    assert len(regfile._rwregs) == 4
    assert len(regfile._roregs) == 2


def test_register_file(args=None):
    global regfile
    args = tb_default_args(args)

    # top-level signals and interfaces
    clock = Clock(0, frequency=50e6)
    reset = Reset(0, active=1, async=False)
    glbl = Global(clock, reset)
    regbus = Wishbone(glbl) 

    @myhdl.block
    def bench_regfile():
        tbdut = memmap_peripheral(glbl, regbus, 0xAA)
        tbor = regbus.interconnect()
        tbmclk = clock.gen(hticks=5)
        asserr = Signal(bool(0))

        mon_ack = Signal(bool(0))

        @always_comb
        def tbmon():
            mon_ack.next = regbus.ack_o

        regdef = regfile.get_regdef()

        @instance
        def tbstim():
            try:
                yield delay(100)
                yield reset.pulse(110)
                yield clock.posedge
                
                for k, reg in regdef.items():
                    if reg.access == 'ro':
                        yield regbus.readtrans(reg.addr)
                        rval = regbus.get_read_data()
                        assert rval == reg.default, \
                            "ro: {:02x} != {:02x}".format(rval, reg.default)
                    else:
                        wval = randint(0, (2**reg.width)-1)
                        yield regbus.writetrans(reg.addr, wval)
                        for _ in range(4):
                            yield clock.posedge
                        yield regbus.readtrans(reg.addr)
                        rval = regbus.get_read_data()
                        assert rval == wval, \
                            "rw: {:02x} != {:02x} @ {:04X}".format(
                                rval, wval, reg.addr)
                yield delay(100)
            except AssertionError as err:
                print("@E: %s".format(err))
                traceback.print_exc()
                asserr.next = True
                for _ in range(10):
                    yield clock.posedge
                raise err

            raise StopSimulation

        return tbmclk, tbstim, tbdut, tbmon, tbor

    run_testbench(bench_regfile, args=args)


def test_register_file_bits():
    global regfile
    # top-level signals and interfaces
    clock = Clock(0, frequency=50e6)
    reset = Reset(0, active=1, async=False)
    glbl = Global(clock, reset)
    regbus = Wishbone(glbl) 

    @myhdl.block
    def bench_regfile_bits():
        tbdut = memmap_peripheral_bits(glbl, regbus, 0xAA)
        tbor = regbus.interconnect()
        tbmclk = clock.gen()
        tbrclk = regbus.clk_i.gen()
        asserr = Signal(bool(0))

        @instance
        def tbstim():
            regfile.ok.next = True
            try:
                yield reset.pulse(111)
                yield clock.posedge
                yield clock.posedge           
                truefalse = True
                yield regbus.writetrans(regfile.control.addr, 0x01)
                for _ in range(100):
                    assert regfile.enable == truefalse
                    assert regfile.loop == (not truefalse)
                    yield regbus.readtrans(regfile.control.addr)
                    invertbits = ~intbv(regbus.get_read_data())[8:]
                    yield regbus.writetrans(regfile.control.addr, invertbits)
                    truefalse = not truefalse
                    yield clock.posedge
            except AssertionError as err:
                asserr.next = True
                for _ in range(20):
                    yield clock.posedge
                raise err
            
            raise StopSimulation

        return tbmclk, tbstim, tbdut, tbor, tbrclk

    run_testbench(bench_regfile_bits)


def test_convert():
    clock = Signal(bool(0))
    reset = ResetSignal(0, active=0, async=True)
    mon = Signal(intbv(0)[8:])
    inst = peripheral_top(clock, reset, mon)
    tb_convert(inst)

    
if __name__ == '__main__':
    # @todo: pass args to the testbenches
    # @todo: tb_register_def(tb_args()) ...
    args = tb_args()

    test_register_def()
    test_register_file(args)
    test_register_file_bits()
    test_convert()
