
from __future__ import absolute_import

from myhdl import Signal, SignalType, always_comb
from .regfile import RegisterFile


class ControlStatus(object):
    def __init__(self):
        self._isstatic = False

    @property
    def isstatic(self):
        return self._isstatic

    @isstatic.setter
    def isstatic(self, val):
        self._isstatic = val

    def get_config_bits(self):
        attrs = vars(self)
        cfgbits = {}
        for k, v in attrs.items():
            if isinstance(v, SignalType) and v.config and not v.driven:
                cfgbits[k] = v.initial_value
        return cfgbits

    def default_assign(self):
        raise NotImplemented

    def get_register_file(self):
        """ get the register-file for this control-status object"""
        return build_register_file(self)

    def get_generators(self):
        """ get any hardware logic associated with the cso"""
        return None


def build_register_file(cso):
    """ Build a register file from a control-status object.

    This function will organize all the `SignalType` attributes in
    a `ControlStatus` object into a register file.
    """
    assert isinstance(cso, ControlStatus)
    rf = RegisterFile()

    for k, v in vars(cso):
        if isinstance(v, SignalType):
            pass

    return rf


def assign_config(sig, val):
    keep = Signal(bool(0))
    keep.driven = 'wire'

    @always_comb
    def beh_assign():
        sig.next = val if keep else val
    return beh_assign
