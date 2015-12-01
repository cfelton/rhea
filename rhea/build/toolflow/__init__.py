
from __future__ import absolute_import

from .toolflow import ToolFlow
from .convert import convert

from .altera import Quartus
from .xilinx import ISE
from .xilinx import Vivado
#from lattice import Diamond

from .yosys import Yosys
from .lattice import IceRiver