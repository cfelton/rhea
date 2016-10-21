
from __future__ import print_function, division

from random import randint

import myhdl
from myhdl import Signal, intbv, instance, delay, StopSimulation, now

from rhea.system import Global, Clock, Reset
from rhea.cores.comm import prbs_generate
from rhea.cores.comm import prbs_check
from rhea.utils.test import run_testbench, tb_args, tb_default_args


def test_known_prbs5(args=None):
    args = tb_default_args(args)
    clock = Clock(0, frequency=125e6)
    reset = Reset(0, active=1, async=False)
    glbl = Global(clock, reset)
    prbs = Signal(intbv(0)[8:])

    expected_pattern = (0xC7, 0xAE, 0x90, 0xE6,)

    @myhdl.block
    def bench_prbs5():
        tbdut = prbs_generate(glbl, prbs, order=5, initval=0x1F)
        tbclk = clock.gen(hticks=8000)
        
        @instance 
        def tbstim():
            yield reset.pulse(32)
            yield clock.posedge
            # for debugging, test prints occur after the module prints
            yield delay(1)  
            
            for ii, ep in enumerate(expected_pattern):
                assert prbs == ep
                yield clock.posedge
                # for debugging, test prints occur after the module prints                
                yield delay(1)
                
            yield delay(100)
            raise StopSimulation
                
        return tbdut, tbclk, tbstim
        
    run_testbench(bench_prbs5, timescale='1ps', args=args)
    
        
def test_known_prbs7(args=None):
    args = tb_default_args(args)
    clock = Clock(0, frequency=125e6)
    reset = Reset(0, active=1, async=False)
    glbl = Global(clock, reset)
    prbs = Signal(intbv(0)[8:])

    # computed by hand
    expected_pattern = (0x3F, 0x10, 0x0C, 0xC5, 0x13, 0xCD, 0x95, 0x2F)

    @myhdl.block
    def bench_prbs7():
        tbdut = prbs_generate(glbl, prbs, order=7, initval=0x7F)
        tbclk = clock.gen(hticks=8000)

        @instance
        def tbstim():
            yield reset.pulse(32)
            # there is one zero at the beginning                        
            yield clock.posedge

            for ii, ep in enumerate(expected_pattern):
                yield clock.posedge
                assert prbs == ep                

            yield delay(100)
            raise StopSimulation

        return tbdut, tbclk, tbstim

    run_testbench(bench_prbs7, timescale='1ps', args=args)


def test_prbs_word_lengths(args=None):
    args = tb_default_args(args)
    clock = Clock(0, frequency=125e6)
    reset = Reset(0, active=1, async=False)
    glbl = Global(clock, reset)
    prbs = Signal(intbv(0)[8:])

    @myhdl.block
    def bench_prbs():
        # currently only order 7, 9, 11, 15, 23, and 31 are coded in
        # prbs feedback tap table, limit testing to one of these patterns
        tbdut = prbs_generate(glbl, prbs, order=23)
        tbclk = clock.gen(hticks=8000)

        @instance
        def tbstim():
            yield reset.pulse(32)

            # this test doesn't check the output (bad) simply checks that
            # the module doesn't choke on the various word-lengths
            for ii in range(27):
                yield clock.posedge

            yield delay(100)
            raise StopSimulation

        return tbdut, tbclk, tbstim
        
    for wl in [2**ii for ii in range(11)]:
        prbs = Signal(intbv(0)[wl:])
        run_testbench(bench_prbs, timescale='1ps', args=args)


def test_prbs_check(args=None):
    # @todo: select different parameters: order ...
    args = tb_default_args(args)
    order = 9

    clock = Clock(0, frequency=125e6)
    reset = Reset(0, active=1, async=False)
    glbl = Global(clock, reset)
    prbs = Signal(intbv(0)[8:])
    locked = Signal(bool(0))
    inject_error = Signal(bool(0))
    word_count = Signal(intbv(0)[64:])
    error_count = Signal(intbv(0)[64:])

    @myhdl.block
    def bench_prbs_checker():
        tbgen = prbs_generate(glbl, prbs, inject_error=inject_error,
                              order=order)
        tbdut = prbs_check(glbl, prbs, locked, word_count,
                           error_count, order=order)
        tbclk = clock.gen()

        maxcycles = 2 * ((2**order)-1)
        
        @instance 
        def tbstim():
            yield reset.pulse(32)
            yield clock.posedge

            assert not locked

            for ii in range(maxcycles):
                yield clock.posedge 

            assert locked
            assert error_count == 0

            for ii in range(randint(0, 1000)):
                yield clock.posedge

            assert locked
            assert error_count == 0
            assert word_count > 0
            lwc = int(word_count)

            inject_error.next = True
            yield clock.posedge
            inject_error.next = False
            yield clock.posedge

            assert locked

            for ii in range(randint(0, 1000)):
                yield clock.posedge

            assert locked
            assert error_count == 1
            assert word_count > lwc
            lec = int(error_count)

            inject_error.next = True
            yield clock.posedge
            yield clock.posedge

            for ii in range(2000):
                yield clock.posedge
                if not locked:
                    break
                assert error_count > lec
                lec = int(error_count)

            assert not locked
            inject_error.next = False

            for ii in range(maxcycles):
                yield clock.posedge
            assert locked

            yield delay(100)
            raise StopSimulation 
                
        return tbgen, tbdut, tbclk, tbstim 
        
    run_testbench(bench_prbs_checker, timescale='1ps', args=args)
    
    
def test_conversion(args=None):
    args = tb_default_args(args)
    clock = Clock(0, frequency=125e6)
    reset = Reset(0, active=1, async=False)
    glbl = Global(clock, reset)
    prbs = Signal(intbv(0)[8:])

    # convert the generator
    inst = prbs_generate(glbl, prbs, order=23)
    inst.convert(hdl='Verilog', testbench=False, directory='output')

    # convert the checker
    locked = Signal(bool(0))
    word_count = Signal(intbv(0)[64:])
    error_count = Signal(intbv(0)[64:])

    inst = prbs_check(glbl, prbs, locked, word_count, error_count, order=23)
    inst.convert(hdl='Verilog', testbench=False, directory='output')
    # @todo: add VHDL conversion, currently there is a but
    #        in myhdl 1.0dev that prevents back-to-back conversion


def tb_parser():
    pass


if __name__ == '__main__':
    args = tb_args()   # tb_args(parser=tb_parser())
    test_known_prbs5(args)
    test_known_prbs7(args)
    test_prbs_word_lengths(args)
    test_prbs_check(args)
    test_conversion(args)

