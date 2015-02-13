
import myhdl
from myhdl import instance, delay

class Reset(myhdl.ResetSignal):
    def __init__(self, val, active, async):
        myhdl.ResetSignal.__init__(self,val,active,async)

    def pulse(self, delays=10):
        if isinstance(delays,(int,long)):
            self.next = self.active
            yield delay(delays)
            self.next = not self.active
        elif isinstance(delays,tuple):
            assert len(delays) in (1,2,3), "Incorrect number of delays"
            self.next = not self.active if len(delays)==3 else self.active
            for dd in delays:
                yield delay(dd)
                self.next = not self.val
            self.next = not self.active
        else:
            raise ValueError("%s type not supported"%(type(d)))
