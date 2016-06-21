#
# Copyright (c) 2014-2015 Christopher Felton
#

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import sys
import os
from time import gmtime, strftime
import subprocess
import shlex

from ..toolflow import ToolFlow
from ..convert import convert
from rhea.build.extintf import Clock


_default_pin_attr = {
    '': None,
}


class IceCube(ToolFlow):
    _name = "Lattice IceCube"

    def __init__(self, brd, top=None, path='lattice/'):
        """ """
        super(IceCube, self).__init__(brd=brd, top=top, path=path)
        self.sdc_file = ''
        self._core_file_list = set()
        self._default_project_file = None

    def create_project(self, use='verilog', **pattr):
        self.sbt_file = os.path.join(self.path, self.name+".project")
