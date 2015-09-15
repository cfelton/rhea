
import os
import shutil
from glob import glob
import argparse

def tb_argparser():
    """ common command line arguments
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--trace',action='store_true')
    parser.add_argument('--test',action='store_true')
    parser.add_argument('--convert', action='store_true')
    return parser


def tb_move_generated_files():
    """ move generated files 
    
    This function should be used with caution, it blindly moves 
    all the *.vhd, *.v, and *.png files.  These files typically 
    do not exist in the project except the cosim directories and 
    the documentation directories.  Most of the time it is safe
    to use this function to clean up after a test.
    """
    # move all VHDL files
    for vf in glob('*.vhd'):
        if os.path.isfile(os.path.join('output/vhd/', vf)):
            os.remove(os.path.join('output/vhd/', vf))
        shutil.move(vf, 'output/vhd/')

    # move all Verilog files
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

    nmpth = os.path.join(vcdpath, '{}.vcd'.format(name))
    if os.path.isfile(nmpth):
        os.remove(nmpth)

    # return the VCD path+name minus extension
    return nmpth[:-4]
    
    
def tb_mon_():
    """ """
    pass

