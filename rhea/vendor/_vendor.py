
class Vendor(object):
    def __init__(self):
        self._vendor = None   # altera, lattice, xilinx
        self._model = None    # vendor model

    @property
    def vendor(self):
        return self._vendor

    @vendor.setter
    def vendor(self, v):
        assert v.lower() in ('altera', 'lattice', 'xilinx')
        self._vendor = v.lower()
