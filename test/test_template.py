
from __future__ import print_function, division

# standard library imports
import math
from random import randint
import argparse 

# myhdl import (following is not a complete list of possible
# imports needed)
import myhdl
from myhdl import (Signal, intbv, instance, delay, always_seq, 
                   StopSimulation, Simulation)

# import module(s) being tested and other support things
from rhea.system import Clock, Reset, Global
from rhea.utils.test import run_testbench, tb_args, tb_default_args


# create testbenches, these take an "args" that control how
# the testbench runs, including but not limited to tracing,
# etc. A testbench may contains.  This function will be run 
# by the py.test test runner.  Make sure the default arguments
# are a test case to be run.  Use "test_*" functions to create
# variants with differnt arguments.
def testbench_nameofwhatsbeingtested(args=None):
    """  """
    # if no arguments were passed get the default arguments, one of 
    # the reasons this is done this way is to avoid conflicts with 
    # the py.test test runner, when executed with py.test no CLI 
    # arguments are expected (although the "test_*" might set specific
    # arguments for a test.
    args = tb_default_args(args)
    if not hasattr(args, 'num_loops'):
        args.num_loops = 10
        
    # create signals, models, etc. that are needed for the various
    # stimulus (a testbench may have multiple stimulus tests).
    clock = Clock(0, frequency=50e6)
    reset = Reset(0, active=1, async=False)
    glbl = Global(clock, reset)
    
    sigin = Signal(intbv(0)[8:])
    sigout = Signal(intbv(0)[8:])
    
    # create  a test/stimulus function, this function is passed
    # to the `run_testbench` function.  A single function is used
    # so the signals in the stimulus can be traced.
    @myhdl.block
    def bench_nameofwhatsbeingtested():
        """  """
        # instantiate design under test, etc. 
        tbdut = some_module(glbl, sigin, sigout)
        tbclk = clock.gen()
        
        @instance 
        def tbstim():
            yield reset.pulse(30)
            yield clock.posedge
            
            # perform stimulus and checking
            for ii in range(args.num_loops):
                sigin.next = randint(0, 255)
                yield clock.posedge   # on the edge the new input is capture
                yield delay(1)        # after the edge the output is available
                print("    sigin: {:02X}, sigout: {:02X}".format(int(sigin), int(sigout)))
                assert sigout == sigin
            
            raise StopSimulation
        
        # return the generators (instances() could be used)
        return tbdut, tbclk, tbstim
        
    run_testbench(bench_nameofwhatsbeingtested, args=args)


@myhdl.block
def some_module(glbl, sigin, sigout):
    """ example module to be tested """
    clock, reset = glbl.clock, glbl.reset
    
    @always_seq(clock.posedge, reset=reset)
    def beh():
        sigout.next = sigin
        
    return beh
    
    
# include the "test_*" functions that invoke the above testbench.
# These are the tests that will be run by the py.test testrunner. 
# In many cases the "test_*" functions might set the testbench 
# `args` and other setup and post simulation checks
def test_nameofwhatsbeingtested():
    args = argparse.Namespace(num_loops=23)
    testbench_nameofwhatsbeingtested()
    

# also setup the tests to be run from the script (this file) directly
# without the test runner.  This is useful for development and debugging.`
if __name__ == '__main__':
    # get the default testbench arguments, also test specific arguments 
    # can be added (see tb_parser for more information). 
    args = tb_args()
    testbench_nameofwhatsbeingtested(args)
