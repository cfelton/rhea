#
# Copyright (c) 2015 Christopher Felton
#

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

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
        super(Vivado, self).__init__(brd, top=top, path=path)
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
                        if kp == 'iostandard':
                            ustr += "set_property "
                        else:
                           raise NotImplemented("additional constraints not supported yet")
        ustr += "#\n"

        fid = open(self.xcd_file, 'w')
        fid.write(ustr)
        fid.close()


    def create_flow_script(self):
        fn = os.path.join(self.path, self.name+'.tcl')

        # start with the text string for the TCL script
        tcl = []
        tcl += ["#\n#\n# Vivado implementation script"]
        date_time = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
        tcl += ["# create: {}".format(date_time)]
        tcl += ["# by: {}".format(os.path.basename(sys.argv[0]))]
        tcl += ["#\n#\n"]
        
            
        tcl += ["# set compile directory:"]
        tcl += ["set origin_dir {}".format('.')]

        tcl += ["create_project {} ./{}".format(self.name, self.name)]
        tcl += ["set proj_dir [get_property direcotry [current_project]]"]
        tcl += ["set obj [get_projects {}]".format(self.name)]
        brd = self.brd
        part = "{}{}{}".format(brd.device, brd.package, brd.speed)
        part = part.lower()
        tcl += ["set property \"part\" {} $obj".format(part)]
        
        # add HDL files
        tcl += ["# create sources"]
        for hdl_file in self._hdl_file_list:
            tcl += ["add_files {}".format(hdl_file)]

        with open(fn, 'w') as fp:
            for line in tcl:
                fp.write(line + "\n")
        
        return fn

    def run(self, use='verilog', name=None):
        """ Execute the toolflow """
        self.pathexist(self.path)
        cfiles = convert(self.brd, name=self.name,
                         use=use, path=self.path)
        self.add_files(cfiles)
        self.create_constraints()
        tcl_name = self.create_flow_script()
        cmd = ['vivado', '-mode', 'batch', '-source', tcl_name]
        self.logfn = self._execute_flow(cmd, "build_vivado.log")

        return self.logfn

    def get_utilization(self):
        info = "NotImplemented"
        return info
