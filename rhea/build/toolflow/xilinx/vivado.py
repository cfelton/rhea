#
# Copyright (c) 2015 Christopher Felton
#

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import sys
import os
import platform
import shutil
from time import gmtime, strftime

from rhea.system import Clock
from ..toolflow import ToolFlow
from ..convert import convert


class Vivado(ToolFlow):
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
        self.xdc_file = ''
        self._default_project_file = None

    def create_project(self, use='verilog', **pattr):
        """ Geenrate the Vivado project file
        :param use: use verilog of vhdl
        :param pattr:
        :return:
        """
        pass

    def create_constraints(self):
        self.xdc_file = os.path.join(self.path, self.name+'.xdc')
        ustr = []
        ustr += ["#\n"]

        # find the clocks and create clock constraints
        for port_name, port in self.brd.ports.items():
            if port.inuse and isinstance(port.sig, Clock):
                period = 1/(port.sig.frequency/1e9)
                ustr += ["create_clock -period {} -waveform {{0 {}}} [get_ports {}]".format(
                          period, period//2, port_name)]
                ustr += ["\n"]
        ustr += ["#\n"]

        # setup all the IO constraints, find ports and match pins
        for port_name, port in self.brd.ports.items():
            if port.inuse:
                _pins = port.pins

                for ii, pn in enumerate(_pins):
                    if len(_pins) == 1:
                        pm = "{}".format(port_name)
                    else:
                        pm = "{{ {}[{}] }}".format(port_name, ii)

                    ustr += ["set_property PACKAGE_PIN {} [get_ports {}]".format(
                        str(pn), pm)]
                        
                    # additional pin constraints
                    for kp, vp in port.pattr.items():
                        if kp == 'iostandard':
                            ustr += ["set_property IOSTANDARD {} [get_ports {}]".format(
                                str(vp), pm)]
                        else:
                            raise NotImplementedError("additional constraints not supported yet")
        ustr += ["#\n"]

        with open(self.xdc_file, 'w') as fid:
            for line in ustr:                
                fid.write(line + '\n')




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
        tcl += ["set origin_dir \"{}\"".format(self.escape_path(self.path))]

        project_directory = self.escape_path(os.path.join(self.path, self.name))
        tcl += ["create_project -force {} \"{}\"".format(
            self.name, project_directory)]
        tcl += ["set proj_dir [get_property directory [current_project]]"]
        tcl += ["set obj [get_projects {}]".format(self.name)]
        brd = self.brd
        part = "{}{}{}".format(brd.device, brd.package, brd.speed)
        part = part.lower()
        tcl += ["set_property PART {} $obj".format(part)]
        
        # add HDL files
        tcl += [""]
        tcl += ["# add sources"]
        for hdl_file in self._hdl_file_list:
            tcl += ["add_files \"{}\"".format(self.escape_path(os.path.join(self.path, hdl_file)))]

        tcl += ["read_xdc \"{}\"".format(self.escape_path(self.xdc_file))]

        tcl += [""]
        tcl += ["# build design"]
        synopts = ""
        tcl += ["synth_design -top {} {}".format(self.name, synopts)]
        tcl += ["opt_design"]
        tcl += ["place_design"]
        tcl += ["route_design"]
        tcl += ["report_timing_summary -file \"{}\"".format(
            self.escape_path(os.path.join(self.path, self.name+'_timing.rpt')))]
        tcl += ["write_bitstream -force \"{}\"".format(
            self.escape_path(os.path.join(self.path, self.name+'.bit')))]

        tcl += ["quit"]

        with open(fn, 'w') as fp:
            for line in tcl:
                fp.write(line + "\n")
        
        return fn

    def create_program_script(self):
        tcl = []
        # >> open_hw_target [lindex [get_hw_targets -of_objects [get_hw_servers localhost]] 0]
        # >> set_property PROGRAM.FILE {xilinx/zybo/zybo.runs/impl_1/zybo.bit} [lindex [get_hw_devices] 1]
        # >> current_hw_device [lindex [get_hw_devices] 1]
        # >> refresh_hw_device -update_hw_probes false [lindex [get_hw_devices] 1]
        # >> set_property PROBES.FILE {} [lindex [get_hw_devices] 1]
        # >> set_property PROGRAM.FILE {xilinx/zybo/zybo.runs/impl_1/zybo.bit} [lindex [get_hw_devices] 1]
        # >> program_hw_devices [lindex [get_hw_devices] 1]
        # >> refresh_hw_device [lindex [get_hw_devices] 1]

    def run(self, use='verilog', name=None):
        """ Execute the toolflow """
        self.pathexist(self.path)
        cfiles = convert(self.brd, name=self.name,
                         use=use, path=self.path)
        self.add_files(cfiles)
        self.create_constraints()
        tcl_name = self.create_flow_script()
        binary_name = 'vivado'
        if platform.system() == 'Windows':
            binary_name += '.bat'

        cmd = [binary_name, '-mode', 'batch', '-source', tcl_name]
        self.logfn = self._execute_flow(cmd, "build_vivado.log")

        # @todo: refactor into a cleanup function
        for frm in ("vivado.log", "vivado.jou",):
            if os.path.isfile(os.path.join(self.path, frm)):
                os.remove(os.path.join(self.path, frm))
            shutil.move(frm, self.path)

        return self.logfn

    def get_utilization(self):
        info = "NotImplemented"
        return info
