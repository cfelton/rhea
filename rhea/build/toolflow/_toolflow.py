#
# Copyright (c) 2014-2015 Christopher Felton
#

from __future__ import division
from __future__ import print_function

import os

class _toolflow(object): 
    def __init__(self, brd, top=None, name=None, path='.'):
        """
        Provided a myhdl top-level module and board definition
        
        This is the base-class for the various FPGA toolchains,
        each toolchain will require a specific implementation, 
        this base-class provides the common features and defines
        the function each toolflow needs to implement.

        Arguments
          top  : myhdl top-level module
          brd  : 
        """

        self._path = path

        # set the brd def top-level
        if top is not None:
            brd.set_top(top) 
        self.brd = brd

        # determing a name for this run, should be the brd def
        # name, or the top-level name, or user specified name.
        # This name should be applied to the file names, project
        # name, and the top-level (converted) module name.
        # the _fpga object (brd def) will determine if the board
        # name of top-level is used
        self.name = brd.top_name if name is None else name
        self._hdl_file_list = set()
        self.logfn = None
        
    @property
    def path(self):
        return self._path
    
    @path.setter
    def path(self, p):
        self._path = p

    def pathexist(self, pth):
        if os.path.isfile(pth):
            pth,fn = os.path.split(pth)
        fpth = ''
        path_split = os.path.split(pth)
        for ppth in pth.split(os.path.sep):
            fpth = os.path.join(fpth,ppth)
            if not os.path.isdir(fpth):
                print("path create %s" % (fpth,))
                os.mkdir(fpth)

        return os.path.isdir(pth)
        
    def set_default_project_file(self, filename=None):
        self._default_project_file = filename

    def create_project(self, **pattr):
        """ Create a project file if needed
        """
        pass

    def create_flow_script(self):
        """ Create the tool-flow script  if needed.
        """
        pass

    def create_constraints(self):
        """ Create the constraints
        """
        pass

    def add_files(self, fn):
        """ Add additional files to the tool-flow
        """
        if isinstance(fn, str):
            fn = {fn}
        if isinstance(fn, (list, tuple, set)):
            if not all(isinstance(ff, str) for ff in fn):
                raise ValueError("Individual filenames must be strings")
        else:
            raise ValueError("Argument must be a string or a list/tuple/set of strings")
            
        self._hdl_file_list.update(set(fn))

    def add_cores(self, fn):
        """ Add vendor specific cores
        """

    def run(self, use='verilog', name=None):
        """ Execute the tool-flow

          use  : indicated if Verilog or VHDL should be used.
          name : user supplied name for project and top-level
        """
        raise NotImplemented()

    def program(self):
        """ Program the board with the bit-stream
        """
        raise NotImplemented()