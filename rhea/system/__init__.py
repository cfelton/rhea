
from __future__ import absolute_import

# these are mainly used by the tests and simulation
from ._const import timespec
from ._const import ticks_per_ns

# small wrappers to include specific attributes
from ._clock import Clock
from ._reset import Reset
from ._glbl import Global

from .regfile._regfile import RegisterBits
from .regfile._regfile import Register
from .regfile._regfile import RegisterFile

# different buses supported by the register file interface
from .memmap._memmap import MemMap
from .memmap._barebone import Barebone
from .memmap._wishbone import Wishbone
from .memmap._avalonmm import AvalonMM
from .memmap._axi4 import AXI4

# streaming interfaces
from .fifobus._fifobus import FIFOBus
