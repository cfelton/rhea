
import os
import sys
import shutil
from glob import glob
import argparse

import pytest
import myhdl


skip_long_sim_test = pytest.mark.skipif(reason="long running tests")
if hasattr(sys, '_called_from_test'):
    skip_long_sim_test = pytest.mark.skipif(
        not pytest.config.getoption("--runlong"),
        reason="long running tests, needs --runlong option to run"
    )


def run_testbench(bench, timescale=None, args=None):
    """ run (simulate) a testbench
    The args need to be retrieved outside the testbench else the test
    will fail with the pytest runner, if no args are passed a default
    will be used.

    Arguments:
        bench (func): The testbench stimulus function, this is the
            top-level myhdl block in the simulation.
        timescale (str): The timescale to use in the simulation, this
            is set in the VCD file.  If this argument is not set no
            timescale is used and the fast clock is set to a period
            of 10 simulation step.
        args (Namespace): Additional configuration arguments
            .trace: enable VCD tracing
    """
    if args is None:
        args = argparse.Namespace(trace=False)
    dr, nm = tb_clean_vcd(bench.__name__)

    inst = bench()
    if args.trace:
        timescale = '' if timescale is None else timescale
        # the myhdl.Block.config_sim is incomplete need to
        # use a mix of the config_sim and old func attributes
        myhdl.traceSignals.name = nm
        myhdl.traceSignals.directory = dr
        myhdl.traceSignals.timescale = timescale
        inst.config_sim(trace=True)

    inst.run_sim()
    del inst


def tb_convert(inst):
    if not os.path.isdir('output/ver/'):
        os.makedirs('output/ver/')
    inst.convert(hdl='Verilog', directory='output/ver')

    if not os.path.isdir('output/vhd/'):
        os.makedirs('output/vhd/')
    inst.convert(hdl='VHDL', directory='output/vhd')


def _tb_argparser(tests=None, parser=None):
    """ common command line arguments 
    Testbenches can use this function to retrieve a parser with the 
    default options.  The testbench can add specific command-line 
    options to the parser and then send to `tb_args`.
    
    Example:
        parser = tb_argparser()
        parser.add_argument('--num_loops', default=10, type=int)
        args = tb_args(parser=parser)
    """
    if parser is None:
        parser = argparse.ArgumentParser()
    parser.add_argument('--trace', action='store_true')
    parser.add_argument('--convert', action='store_true')
    if tests is not None and 'all' not in tests:
        tests += ['all']
    parser.add_argument('--test', choices=tests,
                        help="select the test to run")
    return parser


def tb_args(tests=None, parser=None):
    """ Retrieve the command-line arguments """
    parser = _tb_argparser(tests=tests, parser=parser)
    return parser.parse_args()
    
    
def tb_default_args(args=None):
    """ Set the default arguments 
    This is used when no command-line arguments are passed, this function
    will fill in the defaults are add expected arguments to an incomplete 
    args namespace.  This is commonly included at the top of a testbench.
    """
    if args is None:
        args = argparse.Namespace(trace=False, convert=False)
    else:
        if not hasattr(args, 'trace'):
            args.trace = False
        if not hasattr(args, 'convert'):
            args.convert = False
            
    return args 


def tb_move_generated_files():
    """ move generated files 
    
    This function should be used with caution, it blindly moves 
    all the *.vhd, *.v, and *.png files.  These files typically 
    do not exist in the project except the cosim directories and 
    the documentation directories.  Most of the time it is safe
    to use this function to clean up after a test.
    """
    # move all VHDL files
    if not os.path.isdir('output/vhd'):
        os.makedirs('output/vhd/')
    for vf in glob('*.vhd'):
        if os.path.isfile(os.path.join('output/vhd/', vf)):
            os.remove(os.path.join('output/vhd/', vf))
        shutil.move(vf, 'output/vhd/')

    # move all Verilog files
    if not os.path.isdir('output/ver'):
        os.makedirs('output/ver/')
    for vf in glob('*.v'):
        if os.path.isfile(os.path.join('output/ver/', vf)):
            os.remove(os.path.join('output/ver/', vf))
        shutil.move(vf, 'output/ver/')
        
    # move all png files 
    for pf in glob('*.png'):
        if os.path.isfile(os.path.join('output/png/', pf)):
            os.remove(os.path.join('output/png/', pf))
        shutil.move(vf, 'output/png/')


def tb_clean_vcd(name):
    """ clean up vcd files """
    vcdpath = 'output/vcd'
    if not os.path.isdir(vcdpath):
        os.makedirs(vcdpath)

    for vv in glob(os.path.join(vcdpath, '*.vcd.*')):
        os.remove(vv)

    name = '{}.vcd'.format(name)
    nmpth = os.path.join(vcdpath, name)
    if os.path.isfile(nmpth):
        os.remove(nmpth)

    # return the VCD path+name minus extension
    return vcdpath, name[:-4]
    
    
def tb_mon_():
    """ """
    pass
