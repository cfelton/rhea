#
# Copyright (c) 2015 Christopher Felton
#

from __future__ import division
from __future__ import print_function
from __future__ import absolute_imports

import sys
import os
from time import gmtime, strftime
import subprocess
from pprint import pprint

from .._toolflow import _toolflow
from .._convert import convert
from ..._fpga import _fpga


class Vivado(_toolflow):
    _name = "Xilinx Vivado"
    def __init__(self, brd, top=None, path='./xilinx/'):
        """
        Given a top-level module (function) and a board definition
        create an instance of the Vivado tool-chain.

        :param brd: board definition
        :param top: top-level module (function)
        :param path: path for all the intermediate files
        :return:
        """
        _toolflow.__init__(self, brd, top=top, path=path)
        self.xcf_file = ''
        self._default_project_file = None

    def create_project(self, use='verilog', **pattr):
        """ Geenrate the Vivado project file
        :param use: use verilog of vhdl
        :param pattr:
        :return:
        """
        self.xcl_file = os.path.join(self.path, self.name+'.tcl')
        xpr = ''

        # file list

    def create_constraints(self):
        self.xcf_file = os.path.join(self.path, self.name+'.xcf')
        ustr = ""
        ustr += "#\n"

        # find the clocks and create clock constraints
        for port_name, port in self.brd.ports.items():
            if port.inuse and isinstance(port.sig, Clock):
                ustr += "create_clock -frequency {} [get_ports {}]".format(
                        port.sig.frequency, port_name)
                ustr += "\n"
        ustr += "#\n"

        # setup all the IO constraints, find ports and match pins
        for port_name, port in self.brd.ports.items():
            if port.inuse:
                _pins = port.pins

                for ii, pn in enumerate(_pins):
                    ustr += "set_property PACKAGE_PIN {} [get_pins {}".format(
                            str(pn), port_name)

                    # additional pin constraints
                    for kp, vp in port.pattr.items():
                        print(kp, vp)
                        raise NotImplemented("additional constraints not supported yet")
        ustr += "#\n"

        fid = open(self.xcd_file, 'w')
        fid.write(ustr)
        fid.close()
