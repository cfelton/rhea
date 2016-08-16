#
# Copyright (c) 2014-2015 Christopher Felton
#

from __future__ import division
from __future__ import print_function

import sys
import os
from time import gmtime, strftime
import subprocess
from pprint import pprint

from ..toolflow import ToolFlow
from ..convert import convert
from rhea.build import FPGA
from rhea.build.extintf import Clock
from .ise_parse_reports import get_utilization

_default_pin_attr = {
    'NET': None,
    'LOC': None,
    'IOSTANDARD': None,
    'SLEW': None,
    'DRIVE': None
}


class ISE(ToolFlow):
    _name = "Xilinx ISE"
    def __init__(self, brd, top=None, path='xilinx/'):
        """
        Given a top-level module (function) and a board definition
        create an instance of the ISE tool-chain.
        """
        super(ISE, self).__init__(brd=brd, top=top, path=path)
        #self.reports = _ise_parse_reports(self)
        self.ucf_file = ''

    def create_constraints(self):
        self.ucf_file = self.escape_path(os.path.join(self.path, self.name+'.ucf'))
        ustr = ""
        ustr += "#\n"
        for port_name, port in self.brd.ports.items():
            if port.inuse:
                _pins = port.pins

                for ii, pn in enumerate(_pins):
                    if len(_pins) == 1:
                        ustr += "NET \"%s\" " % port_name
                    else:
                        ustr += "NET \"%s<%d>\" " % (port_name, ii)

                    # pure numeric pins need a preceding "p" otherwise
                    # use the string defined
                    if isinstance(pn, str):
                        ustr += "LOC = \"%s\" " % (str(pn))
                    else:
                        ustr += "LOC = \"p%s\" " % (str(pn))

                    # additional pin parameters
                    for kp, vp in port.pattr.items():
                        if kp.lower() in ("pullup",) and vp is True:
                            ustr += " | %s " % kp
                        else:
                            ustr += " | %s = %s " % (kp, vp)
                    ustr += ";\n"

        ustr += "#\n"

        # @todo: loop through the pins again looking for clocks
        for port_name, port in self.brd.ports.items():
            if port.inuse and isinstance(port.sig, Clock):
                period = 1 / (port.sig.frequency / 1e9)
                ustr += "NET \"%s\" TNM_NET = \"%s\"; \n" % (port_name, port_name)
                ustr += "TIMESPEC \"TS_%s\" = PERIOD \"%s\" %.7f ns HIGH 50%%;" \
                        % (port_name, port_name, period)
                ustr += "\n"
        ustr += "#\n"

        fid = open(self.ucf_file, 'w')
        fid.write(ustr)
        fid.close()
        # @todo: log setup information
        #print(ustr)

        
    def create_flow_script(self):
        """ Create the ISE control script
        """
        # start with the text string for the TCL script
        self.tcl_script = '#\n#\n# ISE implementation script\n'
        date_time = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
        self.tcl_script += '# create: %s\n' % \
                           date_time
        self.tcl_script += '# by: %s\n' % \
                           os.path.basename(sys.argv[0])
        self.tcl_script += '#\n#\n'
        
        fn = self.escape_path(os.path.join(self.path, self.name+'.tcl'))
            
        self.tcl_script += '# set compile directory:\n'
        self.tcl_script += 'set compile_directory %s\n' % '.'

        if self.name:
            self.tcl_script += 'set top_name %s\n' % self.name
            self.tcl_script += 'set top %s\n' % self.name

        self.tcl_script += '# set Project:\n'
        self.tcl_script += 'set proj %s\n' % self.name

        # @note: because the directory is changed everything
        #        is relative to self.path
        self.tcl_script += '# change to the directory:\n'
        self.tcl_script += 'cd %s\n' % self.escape_path(self.path)

        # @todo: verify UCF file exists
        bdir, ucffn = os.path.split(self.ucf_file)
        self.tcl_script += '# set ucf file:\n'
        self.tcl_script += 'set constraints_file %s\n' % ucffn

        self.tcl_script += '# set variables:\n'
        pj_fn = self.name + '.xise'
        # Create or open an ISE project (xise?)
        print('Project name : %s ' % pj_fn)
        pjfull = os.path.join(self.path, pj_fn)

        # let the TCL file be the master file, always create
        # a new project.  If a user uses this to "bootstrap"
        # the need to take care to rename the project if modfied
        # else it will be overwritten.
        if os.path.isfile(pjfull):
            os.remove(pjfull)
            #    self.tcl_script += 'project open %s \n' % (pj_fn)
        #else:
        self.tcl_script += 'project new %s\n' % self.escape_path(pj_fn)

        if self.brd.family:
            self.tcl_script += 'project set family %s\n' % self.brd.family
            self.tcl_script += 'project set device %s\n' % self.brd.device
            self.tcl_script += 'project set package %s\n' % self.brd.package
            self.tcl_script += 'project set speed %s\n' % self.brd.speed

        # add the hdl files
        self.tcl_script += '\n'
        self.tcl_script += '# add hdl files:\n'
        self.tcl_script += 'xfile add %s\n' % ucffn
        for hdl_file in self._hdl_file_list:
            self.tcl_script += 'xfile add %s\n' % hdl_file
       
        self.tcl_script += '# test if set_source_directory is set:\n'
        self.tcl_script += 'if { ! [catch {set source_directory'
        self.tcl_script += ' $source_directory}]} {\n'
        self.tcl_script += '  project set "Macro Search Path"\n'
        self.tcl_script += ' $source_directory -process Translate\n'
        self.tcl_script += '}\n'

        # @todo : need an elgent way to manage all the insane options, 90% 
        #         of the time the defaults are ok, need a config file or 
        #         something to overwrite.  These should be in a dict or
        #         refactored or something

        # always create the binary file as well
        self.tcl_script += "project set \"Create Binary Configuration " \
                           "File\" \"true\" -process \"Generate " \
                           "Programming File\"\n "
        
        # see if the JTAG start-up clock should be used
        if (hasattr(self.brd, "no_startup_jtag_clock") and
            self.brd.no_startup_jtag_clock):
            pass
        else:
            self.tcl_script += "project set \"FPGA Start-Up Clock\" " \
                               "\"JTAG Clock\"" \
                               " -process \"Generate Programming File\" \n"

        # run the implementation
        self.tcl_script += '# run the implementation:\n'
        self.tcl_script += 'process run "Synthesize" \n'
        self.tcl_script += 'process run "Translate" \n'
        self.tcl_script += 'process run "Map" \n'
        self.tcl_script += 'process run "Place & Route" \n'
        self.tcl_script += 'process run "Generate Programming File" \n'
        # close the project
        self.tcl_script += '# close the project:\n'
        self.tcl_script += 'project close\n'

        fid = open(fn, 'w')
        fid.write(self.tcl_script)
        fid.close()
            
        return fn

    def run(self, use='verilog', name=None):
        """ Execute the tool-flow """

        self.pathexist(self.path)

        # convert the top-level
        cfiles = convert(self.brd, name=self.name, 
                         use=use, path=self.path)
        self.add_files(cfiles)

        # create the ISE files to run the toolflow
        self.create_constraints()
        tcl_name = self.create_flow_script()

        cmd = ['xtclsh', tcl_name]
        self.logfn = self._execute_flow(cmd, "build_ise.log")

        return self.logfn


    def get_utilization(self):
        info = get_utilization(self.logfn)
        return info

