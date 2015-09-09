#
# Copyright (c) 2006-2013 Christopher L. Felton
#

import collections
from random import randint
import traceback

from myhdl import *

from rhea.system import Clock
from rhea.system import Reset
from rhea.system import Global
from rhea.system import RegisterFile
from rhea.system import Register
from rhea.system import Wishbone

from rhea.utils.test import *


regdef = None
regfile = None


def _create_mask(n):
    m = 1
    for _ in range(n):
        m = (m << 1) | 1
    return m


def _create_test_regfile():
    global regdef
    regdef = collections.OrderedDict()
    # --register 0--
    reg = Register('control', 0x0018, 8, 'rw', 0)
    reg.comment = "register 0"
    reg.add_named_bits('enable', slice(1, 0))  # read-only namedbit
    reg.add_named_bits('loop', slice(2, 1))    # read-only namedbit
    regdef[reg.name] = reg
    
    # -- more registers register --
    for addr, default in zip((0x20, 0x40, 0x80),
                             (0xDE, 0xCA, 0xFB)):
        reg = Register('reg%s' % (addr,), addr, 8, 'rw', default)
        regdef[reg.name] = reg

    # -- read only register --
    reg = Register('regro', 0x100, 8, 'ro', 0xAA)
    regdef[reg.name] = reg

    # another read only register, with named bits
    reg = Register('status', 0x200, 8, 'ro', 0)
    reg.add_named_bits('error', slice(1, 0))  # bit 0, read-write namedbit
    reg.add_named_bits('ok', slice(2, 1))     # bit 1, read-write namedbit
    reg.add_named_bits('cnt', slice(8, 2))    # bits 7-2, read-write namedbit
    regdef[reg.name] = reg

    regfile = RegisterFile(regdef)
    return regfile


def m_per_top(clock, reset, mon):
    glbl = Global(clock, reset)
    wb = Wishbone(glbl)
    #gpm = wb.m_controller(wb)
    gp1 = m_per(glbl, wb, mon)
    return gp1


def m_per(glbl, regbus, mon):
    global regfile
    regfile = _create_test_regfile()
    g_regfile = regbus.m_per_interface(glbl, regfile)
    clock, reset = glbl.clock, glbl.reset

    ## all "read-only" (status) bits if needed
    @always_seq(clock.posedge, reset=reset)
    def rtl_roregs():
        if regfile.regro.rd:
            regfile.regro.next = mon
        
    return g_regfile #, rtl_roregs


def m_per_bits(glbl, regbus, mon):
    global regfile
    regfile = _create_test_regfile()
    g_regfile = regbus.m_per_interface(glbl, regfile)
    count = modbv(0, min=0, max=1)
    clock, reset = glbl.clock, glbl.reset
    ## all "read-only" (status) bits if needed

    @always(clock.posedge)
    def rtl_roregs():
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
        
    return g_regfile, rtl_roregs


def test_register_def():
    regfile = _create_test_regfile()
    assert len(regfile._rwregs) == 4
    assert len(regfile._roregs) == 2


def test_register_file():
    global regfile
    # top-level signals and interfaces
    clock = Clock(0, frequency=50e6)
    reset = Reset(0, active=1, async=False)
    glbl = Global(clock, reset)
    regbus = Wishbone(glbl) 

    def _test_rf():
        tb_dut = m_per(glbl, regbus, 0xAA)
        tb_or = regbus.m_per_outputs()
        tb_mclk = clock.gen()
        #tb_rclk = regbus.clk_i.gen()
        asserr = Signal(bool(0))

        mon_ack = Signal(bool(0))

        @always_comb
        def tbmon():
            mon_ack.next = regbus.ack_o
        
        @instance
        def tb_stim():
            try:
                yield delay(100)
                yield reset.pulse(111)

                for k, reg in regdef.items():
                    if reg.access == 'ro':
                        yield regbus.read(reg.addr)
                        rval = regbus.get_read_data()
                        assert rval == reg.default, \
                            "ro: {:02x} != {:02x}".format(rval, reg.default)
                    else:
                        wval = randint(0, (2**reg.width)-1)
                        yield regbus.write(reg.addr, wval)
                        for _ in range(4):
                            yield clock.posedge
                        yield regbus.read(reg.addr)
                        rval = regbus.get_read_data()
                        assert rval == wval, \
                            "rw: {:02x} != {:02x}".format(rval, wval)
                yield delay(100)
            except AssertionError as err:
                print("@E: %s".format(err))
                traceback.print_exc()
                asserr.next = True
                for _ in range(10):
                    yield clock.posedge
                raise err

            raise StopSimulation

        return tb_mclk, tb_stim, tb_dut, tbmon, tb_or  #, tb_rclk

    vcd = tb_clean_vcd('_test_rf')
    traceSignals.name = vcd
    g = traceSignals(_test_rf)
    Simulation(g).run()


def test_register_file_bits():
    global regfile
    # top-level signals and interfaces
    clock = Clock(0, frequency=50e6)
    reset = Reset(0, active=1, async=False)
    glbl = Global(clock, reset)
    regbus = Wishbone(glbl) 

    def _test():
        tb_dut = m_per_bits(glbl, regbus, 0xAA)
        tb_or = regbus.m_per_outputs()
        tb_mclk = clock.gen()
        tb_rclk = regbus.clk_i.gen()
        asserr = Signal(bool(0))

        @instance
        def tb_stim():
            regfile.ok.next = True
            try:
                yield reset.pulse(111)
                yield clock.posedge
                yield clock.posedge           
                truefalse = True
                yield regbus.write(regfile.control.addr, 0x01)
                for _ in range(100):
                    assert regfile.enable == truefalse
                    assert regfile.loop == (not truefalse)
                    yield regbus.read(regfile.control.addr)
                    yield regbus.write(regfile.control.addr,
                                       ~regbus.get_read_data())
                    truefalse = not truefalse
                    yield clock.posedge
            except AssertionError as err:
                asserr.next = True
                for _ in range(20):
                    yield clock.posedge
                raise err
            
            raise StopSimulation

        return tb_mclk, tb_stim, tb_dut, tb_or, tb_rclk

    vcd = tb_clean_vcd('_test')
    traceSignals.name = vcd
    g = traceSignals(_test)
    Simulation(g).run()


def test_convert():
    clock = Signal(bool(0))
    reset = ResetSignal(0, active=0, async=True)
    mon = Signal(intbv(0)[8:])
    toVerilog(m_per_top, clock, reset, mon)
    toVHDL(m_per_top, clock, reset, mon)

    
if __name__ == '__main__':
    #parser = tb_arparser()
    #args = parser.parse_args()
    
    test_register_def()
    test_register_file()
    test_register_file_bits()
    test_convert()
    

