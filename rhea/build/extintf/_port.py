
import myhdl

class Port(object):
    """ generic port definitions 
    A port is a "signal" in a top-level HDL module.  The ports
    are mapped to pins on physical devices.  This object is used
    to encapsulate all the attributes of an FPGA pin and associate
    it with a port.
    """

    def __init__(self, name, pins, sigtype=None, **pattr):
        """ relate a port to a device pins and pin attributes

          name: name for the port
          pins: a list (tuple) of the pins
          sigtype: Signal type
          **pattr: port attributes (vendor specific)
        """
        self.name = name
        if isinstance(pins, (int, str)):
            pins = [pins]
        self.pins = pins
        self.inuse = False

        if sigtype is not None:
            self.sig = sigtype
        elif len(pins) == 1:
            self.sig = myhdl.Signal(bool(0))
        else:
            self.sig = myhdl.Signal(myhdl.intbv(0)[len(pins):])

        # device specific arguments, when the pin assignment
        # list is created the following will be used to create
        # the UCF,TCL,SDC,etc. files.
        self.pattr = pattr

        # @todo: need to define the common pin attribute in 
        #    a technology agonostic, the tool-chain will convert
        #    to the specific constraints.
        #    drive
        #    pullup

