#
# Copyright (c) 2014-2015 Christopher Felton
#

from __future__ import division
from __future__ import print_function

import os
from string import Template
import subprocess

_default_error_msg = Template("""
ERROR: The $tool flow failed!  
    Error Code: $errcode

    >> $cmd

    See the log file for more information:
    $logfile
    
    Make sure the tool (quartus, ise, vivado, etc.) is installed
    and accessible from the command line.
""")


class ToolFlow(object): 
    _name = "not specified (bug in code)"

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

        # determining a name for this run, should be the brd def
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
            pth, fn = os.path.split(pth)
        if not os.path.isdir(pth):
            os.makedirs(pth)
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
            raise ValueError(
                "Argument must be a string or a list/tuple/set of strings")
            
        self._hdl_file_list.update(set(fn))

    def add_cores(self, fn):
        """ Add vendor specific cores
        """

    def run(self, use='verilog', name=None):
        """ Execute the tool-flow

          use  : indicated if Verilog or VHDL should be used.
          name : user supplied name for project and top-level
        """
        raise NotImplementedError()

    def _execute_flow(self, cmd, logfn=None, logmode='w'):
        logfn = os.path.join(self.path, logfn)
        try:
            assert logfn is not None, "toolflow failed to set logfn"
            assert len(cmd) > 0, "invalid toolflow command {}".format(cmd)
            with open(logfn, logmode) as logfile:
                subprocess.check_call(
                    cmd, stderr=subprocess.STDOUT, stdout=logfile)
        except (subprocess.CalledProcessError, OSError) as err:
            errmsg = _default_error_msg.substitute(
                dict(tool=self._name, cmd=" ".join(cmd),
                     errcode=str(err), logfile=logfn))
            print(errmsg)

        return logfn

    def program(self):
        """ Program the board with the bit-stream
        """
        raise NotImplementedError()

    def escape_path(self, path):
        # Vivado and ISE at least need to have backslashes in their tcl files escaped.
        return path.replace('\\', '\\\\')
