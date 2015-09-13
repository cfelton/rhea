
from __future__ import print_function

import pytest

from myhdl import Signal, intbv

from rhea.system import Clock, Reset, Global
from rhea.cores.video.lcd import LT24Interface
from rhea.cores.video.lcd import lt24lcd

# a video display model to check timing
fr