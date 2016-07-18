#
# Copyright (c) 2014-2015 Christopher Felton
#

import os
import shutil
import inspect
from random import randint
from copy import copy

import myhdl
from myhdl._block import _Block as Block

from .extintf import Port
from .extintf import Clock
from .extintf import Reset


class FPGA(object):
    """ """
    vendor = "" # FPGA vendor, Altera, Xilinx, Lattice
    device = "" # FPGA device type
    family = "" # FPGA family
    _name = None

    # relate ports to the hardware pins
    default_clocks = {}
    default_resets = {}
    default_ports = {}
    default_extintf = {}

    def __init__(self):
        
        # default attributes
        self.top = None        # top-level myhdl module
        self.top_params = None # top-level parameters
        self.top_name = self._name   # resulting name, project name etc.

        self._clocks = {}
        self._resets = {}
        self._ports = {}
        self._extintfs = {}

        # walk through the default settings
        for k, v in self.default_clocks.items():
            self.add_clock(k, **v)
        for k, v in self.default_resets.items():
            self.add_reset(k, **v)
        for k, v in self.default_ports.items():
            self.add_port(k, **v)
        for k, v in self.default_extintf.items():
            self.add_extintf(k, v)

    @property
    def ports(self):
        return self._ports

    def get_port(self, port_name):
        port = None
        if port_name in self._ports:
            port = self._ports[port_name]
        return port

    def has_top(self):
        """ a top-level is set """
        return self.top is not None

    def set_top(self, top, **params):
        self.top = top
        self.top_params = params
        if self.top_name is None:
            self.top_name = top.func_name

    def get_flow(self):
        raise NotImplementedError

    def _remove_embed_attr(self, pins, pattr):
        """ removed an embedded pin attribute def if present.
        """
        for v in pins:
            if isinstance(v, dict):
                pattr = v
                pins.remove(v)
                break
        return pattr

    def add_clock(self, name, frequency=1, pins=None, **pattr):
        if isinstance(pins, (list,tuple)):
            pins = pins[0]
        assert isinstance(pins, (str,int)), "pins type %s" % (type(pins))
        p = Port(name, pins, sigtype=Clock(0, frequency=frequency), **pattr)
        self._clocks[name] = p
        self._ports[name] = p

    def add_reset(self, name, active, async, pins, **pattr):
        assert isinstance(async, bool)
        assert active in (0,1,)
        p = Port(name, pins, 
                 sigtype=Reset(0, active=active, async=async), **pattr)
        # add to the reset and port dicts
        self._resets[name] = p
        self._ports[name] = p

    def add_port(self, name, pins, **pattr):
        """ add a port definition
        
        A port definition maps a port (an HDL top-level signal name)
        to a pin on the physical device including any attributes of 
        the pin / signal.

        Example: 
          brd.add_port("gpio", pins=(23,24,25,26,), pullup=True)

        It is acceptable to have ports with the same names.
        """
        if isinstance(pins, (str, int)):
            pins = [pins,]
        assert isinstance(pins, (list,tuple)), \
            "pins must be a list/tuple of pins (or a single str/int)"
        pins = list(pins)
        pattr = self._remove_embed_attr(pins, pattr)
        # make sure the pin list is a number or string
        for v in pins:
            assert isinstance(v, (str, int))
            
        # @todo: raise an error vs. 
            assert name not in self._ports, \
                "{} already exists in {}".format(name, self._name)
        self._ports[name] = Port(name, pins, **pattr)

    def add_port_name(self, name, port, slc=None, **pattr):
        """ add a new name, *name*, to an existing port, *port*.
        This function is used when the default port name is known
        but not the pins (if the pins are known use add_port).
        A port name is linked to a default port name or a subset
        (slice) is linked to the new name.  

        Example: 
            brd.add_port_name('led', 'wingC', 7)
        where wingC is a 16-bit port bit-vector

        To extract a range from the port, the slice class has to
        be used, example:
            brd.link_port_name('MSB', 'wingC', slice(16,8))
        """
        
        p = self._ports[port]
        if slc is None:
            pins = p.pins
        else:
            if isinstance(slc, (slice, int)):
                pins = p.pins[slc]
            elif isinstance(slc, (list, tuple)):
                pins = []
                for i in slc:
                    if isinstance(i, int):
                        pins.append(p.pins[i])
                    else:
                        pins += list(p.pins[i])
            else:
                raise Exception("slc must be an int, a slice, or a list of these")

        kws = p.pattr.copy()
        kws.update(pattr)
        self.add_port(name, pins, **kws)

    def rename_port(self, port, name, slc=None, **pattr):
        """ rename a *port* to a new *name*
        This function is useful for *bootstrapping*, bootstrapping
        uses the port names that exist in the object and doesn't
        have a method to select from multiple definitions.  Also,
        useful when the top-level HDL has conflicts.
        """        
        pass

    def add_extintf(self, name, extintf):
        """
        """
        self._extintfs[name] = extintf
        # @todo: extract all the ports from the extintf and 
        #    add them to the global port dict
        pass

    def get_portmap(self, top=None, **kwargs):
        """ given a top-level map the port definitions 
        This module will map the top-level MyHDL module ports
        to a board definition.

        Example usage:
            brd = rhea.build..get_board(<board name>)
            portmap = brd.get_portmatp(top=m_myhdl_module)
            myhdl.toVerilog(m_myhdl_module, **portmap)
        """

        if top is not None:
            self.set_top(top)

        # get the top-level ports and parameters
        assert self.top is not None
        pp = inspect.getargspec(self.top.func)

        # all of the arguments (no default values) are treated as
        # ports.  This doesn't mean it needs to be a port but it
        # is convention that ports are the arguments and parameters
        # are keyword arguments.  A parameter can exist in this 
        # list but it can't be empty ...
        # @todo: this needs some more thought, keyword args might 
        #    be ports, need a method to determine.
        hdlports = {}
        if pp.defaults is not None:
            pl = len(pp.args)-len(pp.defaults)
        else:
            pl = len(pp.args)
        for pn in pp.args[:pl]:
            hdlports[pn] = None
        params = {}
        for ii, kw in enumerate(pp.args[pl:]):
            params[kw] = pp.defaults[ii]

        # see if any of the ports or parameters have been overridden
        if self.top_params is not None:
            for k, v in self.top_params.items():
                if k in hdlports:
                    hdlports[k] = v
            for k, v in self.top_params.items():
                if k in params:
                    params[k] = v

        for k, v in kwargs.items():
            if k in hdlports:
                hdlports[k] = v
        for k, v in kwargs.items():
            if k in params:
                params[k] = v

        # @todo: log this information, some parameters can be too large
        #    to be useful dumping to screen (print).
        # log.write("HDL PORTS   %s" % (hdlports,))
        # log.write("HDL PARAMS  %s" % (params,))

        # match the fpga ports to the hdl ports, not if a port is
        # a keyword argument in the top-level this will fail
        # @todo: this matching code needs to be enhanced, this should
        #    always match a top-level port to a port def.
        for port_name,port in self._ports.items():
            if port_name in hdlports:
                hdlports[port_name] = port.sig
                port.inuse = True

        for k, v in hdlports.items():
            assert v is not None, "Error unspecified port %s"%(k)
        
        # combine the ports and params
        pp = hdlports.copy()
        pp.update(params)

        return pp
