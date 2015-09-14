
from __future__ import absolute_import
from __future__ import print_function

import os


class IceRiver(_toolflow, Yosys):
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
        self.pcf_file = ''

    def create_constraints(self):
        self.pcf_file = os.path.join(self.path, self.name+'.pcf')

    def create_flow_script(self):
        """ Simple shell script to execute the flow """
        self.blif_file = os.path.join(self.path, self.name+'.blif')
        self.txt_file = os.path.join(self.path, self.name+'.txt')
        self.bin_file = os.path.join(self.path, self.name+'.bin')
        self.shell_script = os.path.join(self.path, self.name+'.sh')
        
        fn = os.path.join(self.path, self.name+'.sh')
        sh = " "
        sh += "yosys -s {}".format(self.syn_file)
        sh += "arachne-pnr -d 1k -p {} {} -o {}".format(self.pcf_file,
                                                        self.blif_file,
                                                        self.txt_file)
        sh += "icepack {} {}".format(self.txt_file, self.bin_file)

        with open(self.shell_script, 'w') as f:
            f.write()
            
        return

    def run(self, use='verilog', name=None):
        self.pathexist(self.path)
        # converted files
        cfiles = convert(self.brd, name=self.name,
                         use=use, path=self.path)
        self.add_files(cfiles)
        self.create_project(use=use)
        self.logfn = "build_iceriver.log"
        self._execute(self.shell_script)
        
        return self.logfn
    