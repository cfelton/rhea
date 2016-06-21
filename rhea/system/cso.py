
from __future__ import absolute_import
from abc import ABCMeta, abstractmethod
from myhdl import SignalType


class ControlStatusBase(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        """ Base class for control and status classes
        Many complex digital block have control and status interfaces.
        The base class is the base class for the specific control and
        status objects (typically ``ControlStatus``) in a block, the
        control-status-objects (CSO) can be used to dynamically
        interact with the block from other blocks, statically configure,
        or assign to a register-file that can be accessed from a
        memory-mapped bus.
        """
        self._isstatic = False

    @property
    def isstatic(self):
        return self._isstatic

    @isstatic.setter
    def isstatic(self, val):
        self._isstatic = val

    def get_config_bits(self):
        attrs, cfgbits = vars(self), {}
        for k, v in attrs.items():
            if isinstance(v, SignalType) and v.config and not v.driven:
                cfgbits[k] = v.initial_value
        return cfgbits

    @abstractmethod
    def default_assign(self):
        """ A myhdl.block that assigns the control-status defaults.
        For certain synthesis tools the static values of the signals
        need to be assigned.  This will return generators to keep
        the default signals.  If the synthesis tool supports initial
        values, initial values should be used otherwise this can be
        used to assign a static value to a signal.  Note, the synthesis
        tool will generate warnings that the signal is stuck at a
        value - this is desired.

        Returns:
            myhdl generators
        """
        raise NotImplemented

    def get_register_file(self):
        """ get the register-file for this control-status object"""
        # @todo: this function currently lives in memmap.regfile
        # @todo: return build_register_file(self)
        return None

    @abstractmethod
    def instances(self):
        """ get any hardware logic associated with the cso"""
        return None
