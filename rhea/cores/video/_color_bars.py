
from myhdl import *

# color bar template
COLOR_BARS = (
#    r, g, b
    (1, 1, 1,),  # white
    (1, 1, 0,),  # yellow
    (0, 1, 1,),  # cyan
    (0, 1, 0,),  # green
    (1, 0, 1,),  # magenta
    (1, 0, 0,),  # red
    (0, 0, 1,),  # blue
    (0, 0, 0,),  # black
)


def _update_cbars_with_max(P, width):
    global COLOR_BARS

    cbars = [list(clr) for clr in COLOR_BARS]
    cbarvals = [None for _ in range(len(cbars))]

    for cc in range(len(cbars)):
        for ii in range(3):
            if cbars[cc][ii] == 1:
                cbars[cc][ii] = P
        
        # create a single value out of pixel tuple
        val = (cbars[cc][0] << 2*width) + \
              (cbars[cc][1] << width) +   \
              cbars[cc][2]

        cbarvals[cc] = val

    cbarvals = tuple(cbarvals)
    print("Color bar values:")
    for ii in range(len(cbarvals)):
        print("   {:3d}:  {:08X}".format(ii, cbarvals[ii]))

    return cbarvals
    

def m_color_bars(glbl, vmem, resolution=(640, 480), width=10):
    """ generate a color bar pattern
    """
    global COLOR_BARS

    NUM_COLORS, PMAX, res = len(COLOR_BARS), (2**width)-1, resolution

    cbarvals = _update_cbars_with_max(PMAX, width)

    # the width of each boundary
    pw = res[0] / NUM_COLORS
    
    clock, reset = glbl.clock, glbl.reset
    pval = Signal(intbv(0)[3*width:])
    # DEBUG
    ssel = Signal(intbv(0)[32:0])

    @always_comb
    def rtl_pval():
        sel = 0
        for ii in range(NUM_COLORS):
            if vmem.hpxl > (ii*pw):
                sel = ii
        ssel.next = sel
        pval.next = cbarvals[sel]

    W2, W, MASK = 2*width, width, PMAX

    @always_seq(clock.posedge, reset=reset)
    def rtl_rgb():
        # unpack the RGB value
        vmem.red.next   = (pval >> W2) & MASK
        vmem.green.next = (pval >> W) & MASK 
        vmem.blue.next  = pval & MASK

    return rtl_pval, rtl_rgb
