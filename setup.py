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

try:
    from setuptools import setup
    from setuptools import find_packages
except ImportError:
    from distutils.core import setup
    from pkgutil import walk_packages

    import mn

    # many pypy installs don't have setuptools (?)
    def _find_packages(path='.', prefix=''):
        yield prefix
        prefix = prefix + "."
        for _, name, ispkg in walk_packages(path, 
                                            prefix,
                                            onerror=lambda x: x):
            if ispkg:
                yield name
                
    def find_packages():
        return list(_find_packages(mn.__path__, mn.__name__))
    

setup(name        = "minnesota",
      version     = "0.1pre",
      description = "collection of HDL cores ",
      license     = "LGPL",
      platforms   = ["Any"],
      keywords    = "DSP HDL MyHDL FPGA FX2 USB",

      packages    = find_packages(),
      # @todo need to add the examples and test directories,
      # copy it over ...
      )

