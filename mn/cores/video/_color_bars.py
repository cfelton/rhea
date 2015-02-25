
from myhdl import *



cbars = [
#    r, g, b
    [1, 1, 1,],  # white
    [1, 1, 0,],  # yellow
    [0, 1, 1,],  # cyan
    [0, 1, 0,],  # green
    [1, 0, 1,],  # magenta
    [1, 0, 0,],  # red
    [0, 0, 1,],  # blue
    [0, 0, 0,],  # black
]

def _update_cbars_with_max(P, width):
    global cbars
    for cc in range(len(cbars)):
        for ii in range(3):
            if cbars[cc][ii] == 1:
                cbars[cc][ii] = P
        
        # create a single value out of pixel tuple
        val = (cbars[cc][0] << 2*width) + \
              (cbars[cc][1] << width) +   \
              cbars[cc][2]

        cbars[cc] = val

    cbars = tuple(cbars)
    for ii in range(len(cbars)):
        print("%3d:  %08X" % (ii, cbars[ii]))
    

def m_color_bars(dsys, vmem, resolution=(640,480), width=10):
    """ generate a color bar pattern
    """
    global cbars

    NUM_COLORS, PMAX, res = len(cbars), (2**width)-1, resolution
    # for a design there is only one VGA driver it is ok to
    # globally update cbars!
    _update_cbars_with_max(PMAX, width)

    # the width of each boundrary
    pw = res[0] / NUM_COLORS
    
    clock,reset = dsys.clock,dsys.reset
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
        pval.next = cbars[sel]


    W2,W,MASK = 2*width, width, PMAX
    @always_seq(clock.posedge, reset=reset)
    def rtl_rgb():
        # unpack the RGB value
        vmem.red.next   = (pval >> W2) & MASK
        vmem.green.next = (pval >> W) & MASK 
        vmem.blue.next  = pval & MASK
    

    return rtl_pval, rtl_rgb
