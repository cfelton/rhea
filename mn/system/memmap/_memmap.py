
from __future__ import absolute_import
from __future__ import print_function

from copy import deepcopy
from ..regfile import Register

class MemMap(object):
    def __init__(self, data_width, address_width):
        self.data_width = data_width
        self.address_width = address_width
        self.names = {}
        self.regfiles = {}
        

    def add(self, name, rf, base_address=0):
        """ add a peripheral register-file to the bus
        """
        # want a copy of the register-file so that the
        # address can be adjusted.
        arf = deepcopy(rf)

        for k,v in arf.__dict__.iteritems():
            if isinstance(v, Register):
                v.addr += base_address

        if self.regfiles.has_key(name):
            self.names[name] +=1
            name = name.upper() + "_{:03d}".format(self.names[name])
        else:
            self.names = {name : 0}
            name = name.upper() + "_000"

        self.regfiles[name] = arf            
