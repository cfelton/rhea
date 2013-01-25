#
# Copyright (c) 2013 Christopher L. Felton
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from distutils.core import setup

setup(name        = "minnesota",
      version     = "0.1pre",
      description = "collection of HDL cores ",
      packages    = ["mn",
                     "mn.cores",
                     "mn.cores.usb_ext",
                     "mn.cores.usb_ext.fpgalink",
                     "mn.cores.usb_ext.fx2_model",
                     "mn.cores.usb_ext.usbp"],
      license     = "LGPL", 
      platforms   = ["Any"],
      keywords    = "DSP HDL MyHDL"
      # @todo need to add the examples and test directories,
      # copy it over ...
      )

