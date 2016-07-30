

from __future__ import absolute_import

import myhdl
from myhdl import Signal, intbv, instance, enum, always, now 
from PIL import Image
from .video_display import VideoDisplay

from rhea.cores.video.vga.timing_params import get_timing_dict


Info = {
    'hpusle': [],
    'vpulse': [],         
}


class Counters(object):
    def __init__(self):
        self.hcnt, self.vcnt = 0, 0
        self.hsync, self.vsync = 0, 0
        self.hfpcnt, self.hbpcnt = 0, 0
        self.vfpcnt, self.vbpcnt = 0, 0

    def reset(self):
        self.hcnt, self.vcnt = 0, 0
        self.hsync, self.vsync = 0, 0
        self.hfpcnt, self.hbpcnt = 0, 0
        self.vfpcnt, self.vbpcnt = 0, 0


class VGADisplay(VideoDisplay):
    def __init__(self, frequency=50e6, resolution=(640, 480), refresh_rate=60,
                 line_rate=31250, color_depth=(10, 10, 10)):
        """
        """
        super(VGADisplay, self).__init__(resolution, refresh_rate,
                                         line_rate, color_depth)
        self.name = 'vga'
        
        # get the timings for the configuration
        self.td = get_timing_dict(frequency, resolution, refresh_rate, line_rate)
        
        # keep track ~~of a bunch~~ of stuff
        self.info = {'hpusle': [], 'vpulse': [],}

    @myhdl.block
    def process(self, glbl, vga):
        """
        """
        # keep track of the number of updates
        self.update_cnt = 0

        # VGA driver essentially a state-machine with the following
        # states.  Typically implemented as a bunch of counters.
        self.States = enum('INIT', 'DISPLAY', 
                           'HFP', 'HSYNC', 'HBP', 
                           'VFP', 'VSYNC', 'VBP',
                           'END')

        # state table, small function to handle each state
        self.StateFuncs = {
            self.States.INIT: None,
            self.States.DISPLAY: self._state_display,
            self.States.HFP: self._state_hor_front_porch,
            self.States.HSYNC: self._state_hor_sync,
            self.States.HBP: self._state_hor_back_porch,
            self.States.VFP: self._state_ver_front_porch,
            self.States.VSYNC: self._state_ver_sync,
            self.States.VBP: self._state_ver_back_porch,
            self.States.END: None
        }
        
        self.state = self.States.INIT
        counters = Counters()

        # montior signals for debugging
        #_state = Signal(intbv(0, min=0, max=len(self.States)))
        _state = Signal(str(""))
        hcnt = Signal(intbv(0)[16:])
        vcnt = Signal(intbv(0)[16:])
        # end monitors

        @instance
        def g_capture_vga():            
            while True:
                #print(self.state)
                if self.state == self.States.INIT:
                    print("%10d Screen update, %d, in progress" % (now(), self.update_cnt))
                    counters.reset()
                    self.state = self.States.DISPLAY
                elif self.state == self.States.END:
                    self.state = self.States.INIT
                else:
                    yield self.StateFuncs[self.state](glbl, vga, counters)

        # monitor, sample each variable at each clock
        @always(glbl.clock.posedge)
        def g_monitor():
            _state.next = self.state._name
            hcnt.next = counters.hcnt
            vcnt.next = counters.vcnt
                        
        return g_capture_vga, g_monitor

    def _state_display(self, glbl, vga, counters):
        """
        """
        c = counters
        if c.hcnt < self.num_hpxl:
            yield vga.pxlen.posedge
            if vga.state == vga.states.ACTIVE:
                pixel = list(map(int, (vga.red, vga.green, vga.blue,)))
                # print(c.vcnt, c.hcnt)
                #  determine if this is the last pixel for the display
                last = c.hcnt == self.num_hpxl-1 and c.vcnt == self.num_vpxl-1
                self.set_pixel(c.hcnt, c.vcnt, pixel, last)
                c.hcnt += 1
        else:
            c.vcnt += 1
            if c.vcnt == self.num_vpxl:
                self.state = self.States.VFP
            else:
                self.state = self.States.HFP
                c.hfpcnt = 0
        # end

    def _state_hor_front_porch(self, glbl, vga, counters):
        """
        """
        c = counters
        if not vga.hsync:
            self.state = self.States.HSYNC
            c.hsync = 0
        else:                
            # depending on how the "pixel clock" divides into the
            # active area the front-porch could be slightly longer
            # the calculations need to be updated to adjust for this
            # assert vga.state == vga.States.HOR_FRONT_PORCH
            yield glbl.clock.posedge
            c.hfpcnt += 1
        # end

    def _state_hor_sync(self, glbl, vga, counters):
        """
        """
        c = counters
        if vga.hsync:
            self.state = self.States.HBP
            c.hbpcnt = 0
        else:
            yield glbl.clock.posedge
            c.hsync += 1
        # end

    def _state_hor_back_porch(self, glbl, vga, counters):
        """
        """
        c = counters
        if vga.active:
            if c.vcnt >= self.num_vpxl:
                self.state = self.States.VFP
            else:
                c.hcnt = 0
                self.state = self.States.DISPLAY
        else:                
            yield glbl.clock.posedge
            #assert vga.state == vga.States.HOR_BACK_PORCH
            c.hbpcnt += 1
        # end

    def _state_ver_front_porch(self, glbl, vga, counters):
        """
        """
        c = counters
        if not vga.vsync:
            self.state = self.States.VSYNC
        else:
            yield glbl.clock.posedge
            # assert vga.porch == vga.Porch.VER_FRONT
            c.vfpcnt += 1

    def _state_ver_sync(self, glbl, vga, counters):
        """
        """
        c = counters
        if vga.vsync:
            self.state = self.States.VBP
        else:
            yield glbl.clock.posedge
            c.vsync += 1

    def _state_ver_back_porch(self, glbl, vga, counters):
        """
        """
        c = counters
        if vga.active:
            # @todo; copy uvmem to vvmem
            # self.state = self.States.INIT
            self.state = self.States.END
        else:
            yield glbl.clock.posedge
            # assert vga.porch == vga.Porch.VER_FRONT
            c.vbpcnt += 1

