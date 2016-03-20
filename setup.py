#
# Copyright (c) 2013-2015 Christopher L. Felton
#

try:
    from setuptools import setup
    from setuptools import find_packages
except ImportError:
    from distutils.core import setup
    from pkgutil import walk_packages

    import rhea

    # many pypy installs don't have setuptools (?)
    def _find_packages(path='.', prefix=''):
        yield prefix
        prefix=prefix + "."
        for _, name, ispkg in walk_packages(path, 
                                            prefix,
                                            onerror=lambda x: x):
            if ispkg:
                yield name
                
    def find_packages():
        return list(_find_packages(rhea.__path__, rhea.__name__))
    

setup(name="rhea",
      version="0.0.1",    # release 0 or version 0.1
      description="collection of HDL cores ",
      license="MIT",
      platforms=["Any"],
      keywords="HDL MyHDL FPGA",

      packages=find_packages(),
      # @todo need to add the examples and test directories,
      # copy it over ...
      )

