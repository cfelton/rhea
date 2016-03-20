
from __future__ import absolute_import

from abc import ABCMeta, abstractclassmethod

from myhdl import Signal, SignalType, always_comb


class ControlStatusBase(metaclass=ABCMeta):
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

    @abstractclassmethod
    def default_assign(self):
        raise NotImplemented

    def get_register_file(self):
        """ get the register-file for this control-status object"""
        # @todo: this function currently lives in memmap.regfile
        # @todo: return build_register_file(self)
        return None

    @abstractclassmethod
    def get_generators(self):
        """ get any hardware logic associated with the cso"""
        return None


def assign_config(sig, val):
    """
    Arguments:
        sig (Signal): The signals to be assigned to a constant value
        val (int): The constant value
    """
    keep = Signal(bool(0))
    keep.driven = 'wire'

    @always_comb
    def beh_assign():
        sig.next = val if keep else val
    return beh_assign
