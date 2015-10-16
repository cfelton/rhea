
from __future__ import absolute_import

# these are mainly used by the tests and simulation
from ._const import timespec
from ._const import ticks_per_ns

# small wrappers to include specific attributes
from ._clock import Clock
from ._reset import Reset
from ._glbl import Global

from .memmap import RegisterBits
from .memmap import Register
from .memmap import RegisterFile

# different buses supported by the register file interface
from .memmap import MemoryMapped
from .memmap import Barebone
from .memmap import Wishbone
from .memmap import AvalonMM
from .memmap import AXI4Lite

# streaming interfaces
from .fifobus import FIFOBus
