
from __future__ import division

import myhdl
from myhdl import instance, delay

ClockList = []

class Clock(myhdl.SignalType): 
    """
    This is a clock object, it is a thin wrapper around the Signal
    object and provides needed attributes and clock generation for
    testbenches.
    
    @note: As of Jul-2014 this obj is duplicated in myhdl_tools
    """

    def __init__(self, val, frequency=1, timescale='1ns'):
        self._frequency = frequency
        self._period = 1/frequency
        self._timescale = timescale
        self._set_hticks()
        myhdl.SignalType.__init__(self, bool(val))
        ClockList.append(self)

    @property
    def timescale(self):
        return self._timescale
    @timescale.setter
    def timescale(self, t):
        self._timescale = t
        
    @property
    def frequency(self):
        return self._frequency
    @frequency.setter
    def frequency(self, f):
        self._frequency = f
        self._period = 1/f
        self._set_hticks()
        
    @property
    def period(self):
        return self._period

    def _set_hticks(self):
        #self._nts = self._convert_timescale(self._timescale)
        #self._hticks = int(round(self._period/self._nts))
        self._hticks = 3

    def _convert_timescale(self, ts):
        # @todo: need to complete this, ts is in the form
        #        "[0-9]*["ms","us","ns","ps"], parse the text
        #        format and retrieve a numerical value
        # separate the numerical and text        
        nts = 1e9
        return nts

    def gen(self, hticks=None):
        if hticks is None:
            hticks = self._hticks
        else:
            self._hticks = hticks

        #print('hticks %d'%(hticks))
        @instance
        def gclock():
            self.next = False
            while True:
                yield delay(hticks)
                self.next = not self.val

        return gclock
