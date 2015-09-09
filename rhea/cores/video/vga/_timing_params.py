
from __future__ import division
from __future__ import print_function

SUMMERIED = False
def calc_timings(frequency, resolution,
                 refresh_rate=60, line_rate=31250):
    """
    Arguments
    ---------
    frequency : the system clock rate, the clock rate the logic
                is running
    resolution : a two item tuple with the horizontal x veritical
                 number of pixels
    refresh : the refresh rate (vertical rate) in Hz, default=60

    line_rate : the horizontal rate in Hz, default=31,250
    
    Definitions
    -----------
    All of the following are in "counts" but the vendor 
    specifications are usually in us and ms
    A : one full line, ticks
    B : horizontal sync, ticks
    C : horizontal back porch, ticks
    D : RGB pixel , ticks
    E : horizontal front porch, ticks
    
    O : one full screen, ticks
    P : vertical sync, ticks
    Q : vertical back portch, ticks
    R : all lines, ticks
    S : vertical front porch, ticks

    Fixed durations
      horizontal back porch  : ~2us
      horizontal front porch : ~1us
      horizontal sync pulse  : ~4us
      vertical sync pulse    : ~64us
      vertical back porch    : left overs
      vertical front porch   : ~320-340us

    Note: because mfgs could specificy many different values for the 
          porches (at least back in the day) it isn't that useful to 
          try and match many different mfg standards. The porch 
          determines where the pic is on the screen.  Most monitors 
          this can be adjusted on the monitory if the pic is not 
          centered.  The above fixed values for the porches worked 
          on a set of hardware tested.
    """
    global SUMMERIED

    res = resolution
    # generate the periods in microseconds
    period = 1/frequency
    hticks = (1/line_rate)/period
    vticks = (1/refresh_rate)/period

    # the line timing in counts of system clock
    B = round(4e-6/period)     # horizontal pulse width
    C = round(2e-6/period)     # the back porch time
    E = round(1e-6/period)     # the front porch
    D = hticks - sum([B,C,E])  # hsync active (1)
    X = round(D/(res[0]))      # pixel clock count
    A = sum([B,C,D,E])         # ticks for a complete line != line_rate

    P = round(64e-6/period)    # vsync pulse width
    R = res[1] * (B+C+D+E)     # all lines
    S = round(340e-6/period)   # vertical front porch
    Q = vticks - (P + S + R)   # vertical back porch
    O = sum([P, Q, R, S])      # full screen ~= refresh_rate
    # the pixel count (pixel clock)
    Z = res[0]*res[1]

    if not SUMMERIED:
        SUMMERIED = True
        print(" Video parameters in ticks")
        print("   period ........................ %.3f, %.e" % (frequency, 
                                                                period))
        print("   hticks ........................ %.6f" % (hticks))
        print("   vticks ........................ %.6f" % (vticks))
        print("   A: full line: ................. %d, (%.2f Hz)" % (A, 
                                                               1/(A*period)))
        print("   B: horizontal pulse width: .... %d" % (B))
        print("   C: horizontal back porch:...... %d" % (C))
        print("   D: horizontal active: ......... %d" % (D))
        print("   E: horizontal front porch: .... %d" % (E))
        
        print("   O: full screen ................ %d, (%.2f Hz)" % (O, 
                                                               1/(O*period)))
        print("   P: vertical pulse width ....... %d" % (P))
        print("   Q: vertical back porch ........ %d" % (Q))
        print("   R: all lines .................. %d" % (R))
        print("   S: vertical front porch ....... %d" % (S))
        print("   X: pixel clock count .......... %.3f" % (X))
        print("   Z: pixel count: ............... %d" % (Z))

    # @todo: create files for the other languages.
    
    return map(int, (A,B,C,D,E,O,P,Q,R,S,X,Z,))


def get_timing_dict(frequency, resolution,
                    refresh_rate=60, line_rate=31250):
    """ get the VGA timing parameters in a dictionary
    """
    tv = calc_timings(frequency, resolution,
                     refresh_rate, line_rate)
    
    tparams = {'A': tv[0],
               'B': tv[1],
               'C': tv[2],
               'D': tv[2],
               'E': tv[2],
               'O': tv[2],
               'P': tv[2],
               'Q': tv[2],
               'R': tv[2],
               'S': tv[2],
               'X': tv[2],
               'Z': tv[2]}

    return tparams


def dump_params(tv):
    pass