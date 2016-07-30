
from __future__ import division
from __future__ import print_function


SUMMERIED = False
PARAM_ERR_MSG = """Invalid parameter, make sure the refresh rate and line rate
are valid for the resolution {} {}"""


def calc_timings(frequency, resolution,
                 refresh_rate=60, line_rate=31250):
    """
    Arguments:
        frequency: the system clock rate, the clock rate the logic
                   is running
        resolution: a two item tuple with the horizontal x vertical
                   number of pixels
        refresh_rate: the refresh rate (vertical rate) in Hz, default=60

        line_rate : the horizontal rate in Hz, default=31,250
    
    Definitions
    -----------
    All of the following are in "counts" but the vendor 
    specifications are usually in us and ms
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

    Fixed durations
      horizontal back porch  : ~2us
      horizontal front porch : ~1us
      horizontal sync pulse  : ~4us
      vertical sync pulse    : ~64us
      vertical front porch   : ~320-340us
      vertical back porch    : left overs

    Note: because mfgs could specify many different values for the
          porches (at least back in the day) it isn't that useful to 
          try and match many different mfg standards. The porch 
          determines where the pic is on the screen.  Most monitors 
          this can be adjusted on the monitor if the pic is not
          centered.  The above fixed values for the porches worked 
          on a set of hardware tested.
    """
    global SUMMERIED

    # the horizontal spaces are defined in time
    hor_pulse_width = 4e-6
    hor_back_porch = 3e-6
    hor_front_porch = 1.5e-6

    # the vertical spaces are defined in "lines" the value in time
    ver_pulse_width = 2 * (1/line_rate)    # 2 lines
    ver_front_porch = 10 * (1/line_rate)   # 10 lines

    res = resolution

    # base on the parameters get the number of ticks
    period = 1/frequency
    hticks = (1/line_rate)/period
    vticks = (1/refresh_rate)/period

    # the line timing in counts of system clock
    B = round(hor_pulse_width/period)  # horizontal pulse width
    C = round(hor_back_porch/period)   # the back porch time
    E = round(hor_front_porch/period)  # the front porch
    D = hticks - sum([B, C, E])        # hsync active (1)

    X = round(D/(res[0]))              # pixel clock count
    assert X >= 1, "clock is too slow {.3f} MHz".format(frequency)

    A = sum([B, C, D, E])              # ticks for a complete line != line_rate

    P = round(ver_pulse_width/period)  # vsync pulse width
    R = res[1] * (B+C+D+E)             # all lines
    S = round(ver_front_porch/period)  # vertical front porch
    Q = vticks - (P + S + R)           # vertical back porch

    full_screen = sum([P, Q, R, S])
    Q = Q + (full_screen % A)
    F = sum([P, Q, R, S])              # full screen in ticks
    # the pixel count (pixel clock)
    Z = res[0]*res[1]

    if not SUMMERIED:
        SUMMERIED = True
        print(" Video parameters in ticks for {} x {},".format(*res))
        print(" {} Hz line rate and {} Hz refresh rate".format(
            line_rate, refresh_rate))

        print("   period ........................ %.3f, %.e" % (frequency, 
                                                                period))
        print("   hticks ........................ %.6f" % (hticks,))
        print("   vticks ........................ %.6f" % (vticks,))
        print("   A: full line: ................. %d, (%.2f Hz)" % (
            A, 1/(A*period)))
        print("   B: horizontal pulse width: .... %d" % (B))
        print("   C: horizontal back porch:...... %d" % (C))
        print("   D: horizontal active: ......... %d" % (D))
        print("   E: horizontal front porch: .... %d" % (E))
        
        print("   F: full screen ................ %d, (%.2f Hz)" % (
            F, 1/(F*period)))
        print("   P: vertical pulse width ....... %d" % (P))
        print("   Q: vertical back porch ........ %d" % (Q))
        print("   R: all lines .................. %d" % (R))
        print("   S: vertical front porch ....... %d" % (S))
        print("   X: pixel clock count .......... %.3f" % (X))
        print("   Z: pixel count: ............... %d pixels" % (Z))

    params = list(map(int, (A, B, C, D, E, F, P, Q, R, S, X, Z,)))
    keys = "ABCDEFPQRSXZ"
    for k, pp in zip(keys, params):
        assert pp > 0, PARAM_ERR_MSG.format(k, pp)
    
    return params


def get_timing_dict(frequency, resolution,
                    refresh_rate=60, line_rate=31250):
    """ get the VGA timing parameters in a dictionary
    """
    tv = calc_timings(frequency, resolution, refresh_rate, line_rate)
    
    tparams = {'A': tv[0],
               'B': tv[1],
               'C': tv[2],
               'D': tv[2],
               'E': tv[2],
               'F': tv[2],
               'P': tv[2],
               'Q': tv[2],
               'R': tv[2],
               'S': tv[2],
               'X': tv[2],
               'Z': tv[2]}

    return tparams


def dump_params(tv):
    pass