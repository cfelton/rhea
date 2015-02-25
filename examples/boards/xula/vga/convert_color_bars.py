
import os
import argparse

from myhdl import *
from vga_intf import *
from vga_color_bars import m_color_bars

def convert(args):
    dsys = System(frequency=50e6)
    vmem = VideoMemory()
    
    toVerilog(m_color_bars, dsys, vmem, 
              resolution=args.res, width=args.width)

    #toVHDL(m_color_bars, dsys, vmem, 
    #       resolution=args.res, width=args.width)

def get_cli_args():
    parser = argparse.ArgumentParser(description="Convert colobar generator")
    parser.add_argument('--resolution', default="640,480", type=str,
                        help="define the resolution, <hor>x<ver>, e.g. 1280x720")
    parser.add_argument('--width', default=8, type=int,
                        help="define the pixel width in bits")

    args = parser.parse_args()

    res = args.resolution.replace(' ', '')
    res = res.lower()
    args.res = tuple(map(int, res.split('x')))

    return args

if __name__ == '__main__':
    args = get_cli_args()
    convert(args)
            