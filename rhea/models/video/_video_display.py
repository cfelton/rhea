
from array import array
from copy import deepcopy

from myhdl import *
from PIL import Image

from ...cores.video.vga._timing_params import get_timing_dict

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


class VideoDisplay(object):
    def __init__(self, 
                 frequency=50e6,
                 resolution=(640,480,), 
                 refresh_rate = 60,
                 line_rate = 31250,
                 color_depth=(10, 10, 10,)
             ):

        res = resolution
        self.res = resolution
        self.HPXL, self.VPXL = self.res
        if max(color_depth) <= 8:
            arraytype = 'B'
        elif max(color_depth) <= 16:
            arraytype = 'H'
        elif max(color_depth) <= 32:
            arraytype = 'L'

        # create a container to emulate the video display
        # in the process of updating image
        #self.uvmem = [array(arraytype, [0 for _ in range(res[0])])
        #              for _ in range(res[1])]
        self.uvmem = [[None for _ in range(res[0])]
                      for _ in range(res[1])]
        # static image
        #self.vvmem = [array(arraytype, [0 for _ in range(res[0])])
        #              for _ in range(res[1])]
        self.vvmem = [[None for _ in range(res[0])]
                      for _ in range(res[1])]


        self.td = get_timing_dict(frequency, resolution,
                                  refresh_rate, line_rate)

        # keep track of a bunch of stuff
        self.info = {
            'hpusle': [],
            'vpulse': [],         
        }

    def _gen_image(self, framen, frame):
        """
        """
        im = Image.new('RGB', self.res)
        for rr,row in enumerate(frame):
            for cc,rgb in enumerate(row):
                im.putpixel((cc,rr), tuple(rgb))

        im.save('test_vgasys_frame_%d.png' % (framen))

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
                    self.update_cnt += 1
                    self._gen_image(self.update_cnt, self.uvmem)
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
        if c.hcnt < self.HPXL:
            #yield vga.pxlen.posedge if not vga.pxlen else delay(0)
            yield vga.pxlen.posedge
            if vga.state == vga.States.ACTIVE:
                pixel = map(int, (vga.red, vga.green, vga.blue,))
                #print(c.vcnt, c.hcnt)
                self.uvmem[c.vcnt][c.hcnt] = pixel
                c.hcnt += 1
        else:
            c.vcnt += 1
            #yield glbl.clock.posedge
            #yield delay(int(self.td['X']/2))
            if c.vcnt == self.VPXL:
                self.state = self.States.VFP
            else:
                self.state = self.States.HFP
                c.hfpcnt = 0
        #end

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
            # the calculations need to be udpated to adjust for this
            #assert vga.state == vga.States.HOR_FRONT_PORCH
            yield glbl.clock.posedge
            c.hfpcnt += 1
        #end

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
        #end

    def _state_hor_back_porch(self, glbl, vga, counters):
        """
        """
        c = counters
        if vga.active:
            if c.vcnt >= self.VPXL:
                self.state = self.States.VFP
            else:
                c.hcnt = 0
                self.state = self.States.DISPLAY
        else:                
            yield glbl.clock.posedge
            #assert vga.state == vga.States.HOR_BACK_PORCH
            c.hbpcnt += 1
        #end

    def _state_ver_front_porch(self, glbl, vga, counters):
        """
        """
        c = counters
        if not vga.vsync:
            self.state = self.States.VSYNC
        else:
            yield glbl.clock.posedge
            #assert vga.porch == vga.Porch.VER_FRONT
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
            #self.state = self.States.INIT
            self.state = self.States.END
        else:
            yield glbl.clock.posedge
            #assert vga.porch == vga.Porch.VER_FRONT
            c.vbpcnt += 1
