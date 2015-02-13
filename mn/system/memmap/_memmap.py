

class RWData(object):
    def __init__(self):
        self.wval = 0
        self.rval = 0

    def set(self, val):
        self.wval = val

    def get(self):
        return self.rval
