"""
Define common Signal types that can be used to provide additional
information
"""
from myhdl import Signal, SignalType, intbv


class Constants(object):
    def __init__(self, **constargs):
        """ A collection of constants
        """
        # the const can contain int and str convert all to int
        for name, const in constargs.items():
            assert isinstance(name, str)
            assert isinstance(const, (int, bool, intbv, str,)), \
                "Invalid type {}".format(type(const))
            if isinstance(const, str):
                ival = int(const.replace('_', ''), 2)
            else:
                ival = int(const)
            constargs[name] = ival

        # create a set, the set of of constants
        self._constset = set([cc for np, cc in constargs.items()])

        # add the constants to the instance as attributes
        for name, const in constargs.items():
            self.__dict__[name] = const

        self._constants = constargs

    def __len__(self):
        return len(self._constants)

    def __call__(self, val=0):
        cmin, cmax = min(self._constset), max(self._constset)
        return intbv(val, min=cmin, max=cmax+1)


def Signals(sigtype, num_sigs):
    """ Create a list of signals
    Arguments:
        sigtype (bool, intbv): The type to create a Signal from.
        num_sigs (int): The number of signals to create in the list
    Returns:
        sigs: a list of signals all of type `sigtype`

    Creating multiple signals of the same type is common, this
    function helps facilitate the creation of multiple signals of
    the same type.

    The following example creates two signals of bool
        >>> enable, timeout = Signals(bool(0), 2)

    The following creates a list-of-signals of 8-bit types
        >>> mem = Signals(intbv(0)[8:], 256)
    """
    assert isinstance(sigtype, (bool, intbv))
    sigs = [Signal(sigtype) for _ in range(num_sigs)]
    return sigs


class Signal(SignalType):
    def __init__(self, sigtype=0, driven=False, config=False):
        """
        Another Signal object that provides a property to set the
        initial value.  This is a thin wrapper around the myhdl.Signal
        to provide some additional features used during elaboration.

        Note, namespaces need to be used to manage the myhdl.Signal
        and rhea.system.Signal.

        Arguments:
            sigtype (bool, intbv): the type that will be carried by
                the signal, typically a ``bool`` or ``intbv``.
            driven: the signal is driven, typically used to indicate
                a read-only status signal.
            config: the signal is can also be used as a static
                configuration.
        """
        super(Signal, self).__init__(sigtype)
        if driven:
            self.driven = 'reg'
        self.config = config

    @property
    def initial_value(self):
        return self._init

    @initial_value.setter
    def initial_value(self, val):
        # @todo: check the signal type and verify the new initial value
        self._init = val


class Bit(Signal):
    def __init__(self, val=0, driven=False, config=False):
        super(Bit, self).__init__(bool(val), driven, config)

    def __repr__(self):
        return "Bit"


class Byte(Signal):
    def __init__(self, val=0, driven=False, config=False):
        sigtype = intbv(val,)[8:]
        super(Byte, self).__init__(sigtype, driven, config)

    def __repr__(self):
        return "Byte"
