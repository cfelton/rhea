#
# Copyright (c) 2014-2015 Christopher Felton
#

import os
import time
import shutil

import myhdl
from myhdl._block import _Block as Block
from myhdl import toVerilog
from myhdl import toVHDL

from .. import FPGA


def convert(brd, top=None, name=None, use='verilog', path='.'):
    """ Wrapper around the myhdl conversion functions
    This function will use the _fpga objects get_portmap function
    to map the board definition to the 

    Arguments
      top  : top-level myhld module
      brd  : FPGA board definition (_fpga object)
      name : name to use for the generated (converted) file
      use  : User 'verilog' or 'vhdl' for conversion
      path : path of the output files
    """
    assert isinstance(brd, FPGA)

    name = brd.top_name if name is None else name
    pp = brd.get_portmap(top=top)
    inst = brd.top(**pp)

    # convert with the ports and parameters        
    if use.lower() == 'verilog':
        if name is not None:
            myhdl.toVerilog.name = name
        myhdl.toVerilog.no_testbench = True
        # myhdl.toVerilog(brd.top, **pp)
        inst.convert(hdl='Verilog', name=name, testbench=False)
        brd.name = name
        brd.vfn = "%s.v"%(name)
    elif use.lower() == 'vhdl':
        if name is not None:
            myhdl.toVHDL.name = name
        # myhdl.toVHDL(brd.top, **pp)
        inst.convert(hdl='VHDL', name=name)
        brd.name = name
        brd.vfn = "%s.vhd"%(name)
    else:
        raise ValueError("Incorrect conversion target %s"%(use))

    # make sure the working directory exists
    #assert brd.pathexist(brd.path)
    time.sleep(2)

    # copy files etc to the working directory
    tbfn = 'tb_' + brd.vfn
    ver = myhdl.__version__
    # remove special characters from the version
    for sp in ('.', '-', 'dev'):
        ver = ver.replace(sp,'')
    pckfn = 'pck_myhdl_%s.vhd'%(ver)
    for src in (brd.vfn,tbfn,pckfn):
        dst = os.path.join(path, src)
        #print('   checking %s'%(dst))
        if os.path.isfile(dst):
            print('   removing %s'%(dst))
            os.remove(dst)
        if os.path.isfile(src):
            print('   moving %s --> %s'%(src, path))
            try:
                shutil.move(src, path)
            except Exception as err:
                print("skipping %s because %s" % (src, err,))

    if use.lower() == 'verilog':
        filelist = (brd.vfn,)
    elif use.lower() == 'vhdl':
        filelist = (brd.vfn, pckfn,)

    return filelist

    
