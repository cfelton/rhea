
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

def tb_move_v():
    for vf in glob('*.vhd'):
        if os.path.isfile(os.path.join('vhd/',vf)):
            os.remove(os.path.join('vhd/',vf))
        shutil.move(vf, 'vhd/')

    for vf in glob('*.v'):
        if os.path.isfile(os.path.join('ver/',vf)):
            os.remove(os.path.join('ver/',vf))
        shutil.move(vf, 'ver/')

def tb_clean_vcd(name):
    for vv in glob('*.vcd.*'):
        os.remove(vv)

    if os.path.isfile('%s.vcd'%(name)):
        os.remove('%s.vcd'%(name))

