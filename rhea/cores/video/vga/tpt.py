
from rhea import Constants, Clock

# @todo: dump information about the display, the following is a
#        string template that will be filled in with information
#        from the timing parameters.
DISPLAY = """
-----+-------------------------------+-----
     |                               |
     |                               |
-----+-------------------------------+-----
     |                               |
     |                               |
     |                               |
     |                               |
     |                               |
     |                               |
     |                               |
     |                               |
-----+-------------------------------+-----
     |                               |
     |                               |
-----+-------------------------------+-----
"""


def get_line_rate(resolution):
    npixels = resolution[0] * resolution[1]
    # this is the suggested line rate for VGA, the following are line
    # rates that have worked in limited testing other line rates might
    # be more appropriate.
    base_line_rate = 31469

    if npixels > 1600*1200:
        line_rate = 4 * base_line_rate
    elif npixels > 800*600:
        line_rate = 2 * base_line_rate
    else:
        line_rate = base_line_rate

    return int(line_rate)


class VGATimingParameters(object):
    def __init__(self, clock, resolution, refresh_rate=60, line_rate=None):
        """
        Parameters:
            clock: system clock, frequency extracted
            resolution: resolution of the display
            refresh_rate: the refresh rate of the display
            line_rate: (optional)
        """
        assert isinstance(clock, Clock)
        assert isinstance(resolution, tuple)
        assert isinstance(refresh_rate, int)

        self.clock = clock
        self.resolution = resolution
        self.refresh_rate = refresh_rate

        # @todo: calculate the minimum line_rate needed, try to
        #        use common line rates other wise use the minimum
        #        integer line rate.
        if line_rate is None:
            line_rate = get_line_rate(resolution)
        self.line_rate = line_rate
        line_width = 1/line_rate

        # some short hand alias (references)
        res, lr = resolution, line_rate

        # horizontal spaces defined in time
        self._hor_pulse_width = 4e-6
        self._hor_front_porch = 1.5e-6
        # @todo this should be calculated? leftovers?
        self._hor_back_porch = 3e-6

        # vertical spaces defined with "lines" units is time
        self._ver_pulse_width = 2 * (1/lr)    # 2 lines
        self._ver_front_porch = 10 * (1/lr)   # 10 lines

        period = 1/clock.frequency
        hticks, vticks = (1/lr)/period, round((1/refresh_rate)/period)

        # some more short-hand / aliases
        hpw, vpw, vfp = (self._hor_pulse_width, self._ver_pulse_width,
                         self._ver_front_porch,)

        # the timing parameters in ticks
        self._hor_front_porch_ticks = round(self._hor_front_porch/period)  # E
        self._hor_sync_pulse_width_ticks = round(hpw/period)               # B
        self._hor_back_porch_ticks = round(self._hor_back_porch/period)    # C
        assert self._hor_back_porch_ticks > 0
        b, c, e = (self._hor_sync_pulse_width_ticks, self._hor_back_porch_ticks,
                   self._hor_front_porch_ticks)
        self._active_area_ticks = hticks - sum([b, c, e])                  # D
        d = self._active_area_ticks
        x = round(d/res[0])
        assert x >= 1, "clock is too slow {:.3f} MHz".format(clock.frequency/1e6)
        self._full_line_ticks = sum([b, c, d, e])                          # A

        self._ver_sync_pulse_width_ticks = round(self._ver_pulse_width/period)    # P
        self._all_lines_ticks = res[1] * (b+c+d+e)         # R
        self._ver_front_porch_ticks = round(self._ver_front_porch/period)         # S
        p, r, s = (self._ver_sync_pulse_width_ticks,
                   self._all_lines_ticks,
                   self._ver_front_porch_ticks)
        self._ver_back_porch_ticks = vticks - (p + s + r)         # Q
        q = self._ver_back_porch_ticks
        self._full_screen_ticks = sum([p, q, r, s])             # F

        assert q > 0, "line rate is too slow {:.3f} kHz, back porch {}".format(
            line_rate/1e3, q
        )

    def get_named_constants(self):
        """
        hor = horizontal
        ver = vertical

            A : one full line, ticks
            B : horizontal sync pulse width, ticks
            C : horizontal back porch, ticks
            D : RGB pixel active area , ticks
            E : horizontal front porch, ticks

            P : vertical sync pulse width, ticks
            Q : vertical back porch, ticks
            R : all lines, ticks
            S : vertical front porch, ticks

            F : one full screen, ticks

        """
        named_constants = Constants(
            active_area=0,    # active area in ticks
            full_line=0,      # number of ticks in a full line
            all_lines=0,      # number of ticks in all lines (not ver porches)
            full_screen=0,    # number of ticks in a full screen

            hor_sync_pulse=0,
            hor_front_porch=0,
            hor_back_porch=0,

            ver_sync_pulse=0,
            ver_front_porch=0,
            ver_back_porch=0,
        )
        return named_constants

    def _update_parameters(self):
        pass

    def set_horizontal_params(self, pulse_width, front_porch, back_porch):
        pass

    def set_vertical_params(self, pulse_width, front_porch, back_porch):
        pass

    def show_display(self):
        pass