
from __future__ import absolute_import
from __future__ import print_function

import os
import subprocess
import shlex

from ._toolflow import _toolflow
from ._convert import convert
from ._yosys import Yosys
from .._fpga import _fpga
from ..extintf import Clock


class IceRiver(Yosys):
    _name = "Open-source Lattice iCE40"

    def __init__(self, brd, top=None, path='./iceriver/'):
        """
        IceRiver is the (odd) name given to the open-source
        tools available that support (some) lattice devices.
        The toolflow consists of a couple open-source tools:
            - yosys: synthesis tool
            - arachne-pnr: place-n-route tool
            - icepack: conversion to binary (bitstream creation)
            - iceprog:

            http://www.clifford.at/icestorm/
        """
        super(IceRiver, self).__init__(brd=brd, top=top, path=path)
        self.pcf_file = os.path.join(self.path, self.name+'.pcf')
        self.blif_file = os.path.join(self.path, self.name+'.blif')
        self.txt_file = os.path.join(self.path, self.name+'.txt')
        self.bin_file = os.path.join(self.path, self.name+'.bin')
        self.shell_script = os.path.join(self.path, self.name+'.sh')

    def create_constraints(self):
        pcf = " \n"
        pcf += "# pin definitions \n"
        for port_name, port in self.brd.ports.items():
            if port.inuse and isinstance(port.sig, Clock):
                period = 1 / (port.sig.frequency / 1e9)
                # pcf += "create_clock -period {:.7f} [get_ports %s]"

        for port_name , port in self.brd.ports.items():
            if port.inuse:
                pins = port.pins
                for ii, pn in enumerate(pins):
                    if len(pins) == 1:
                        pname = "{}".format(port_name)
                    else:
                        pname = "{}[{}]".format(port_name, ii)
                    pcf += "set_io {} {} \n".format(pname, pn)

        with open(self.pcf_file, 'w') as f:
            f.write(pcf)
        return

    def create_flow_script(self):
        """ Simple shell script to execute the flow """

        fn = os.path.join(self.path, self.name+'.sh')
        sh = " \n"

        #sh += "yosys -s {} \n".format(self.syn_file)
        # the following only works for signle files
        v = [f for f in self._hdl_file_list]
        vfile = os.path.join(self.path, v[0])
        sh += "yosys -p \"synth_ice40 -blif {}\" {}\n".format(
            self.blif_file, vfile)
        
        sh += "arachne-pnr -d 1k -p {} {} -o {} \n".format(self.pcf_file,
                                                           self.blif_file,
                                                           self.txt_file)
        sh += "icepack {} {} \n".format(self.txt_file, self.bin_file)

    
        with open(self.shell_script, 'w') as f:
            f.write(sh)
        os.chmod(self.shell_script, 0o444)
        return

    def run(self, use='verilog', name=None):
        self.pathexist(self.path)
        # converted files
        cfiles = convert(self.brd, name=self.name,
                         use=use, path=self.path)
        self.add_files(cfiles)
        # create_project generates the yosys synth script, this
        # isn't really used (generic yosys script)
        self.create_project(use=use, write_blif=True, ice=True)
        self.create_constraints()
        self.create_flow_script()
        cmd = ['sh', self.shell_script]
        self.logfn = self._execute_flow(cmd, "build_iceriver.log")

        return self.logfn

    def program(self):
        bitfile = os.path.join(self.path, self.bin_file)
        for cmd in self.brd.program_device_cli:
            ucmd = cmd.substitute(dict(bitfile=bitfile))
            self.logfn = "program_iceriver.log"
            self._execute_flow(ucmd)
        return
