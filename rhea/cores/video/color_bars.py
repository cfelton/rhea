
from __future__ import division

import myhdl
from myhdl import Signal, intbv, always_comb, always_seq


# color bar template
COLOR_BARS = (
    # r, g, b
    (1, 1, 1,),  # white
    (1, 1, 0,),  # yellow
    (0, 1, 1,),  # cyan
    (0, 1, 0,),  # green
    (1, 0, 1,),  # magenta
    (1, 0, 0,),  # red
    (0, 0, 1,),  # blue
    (0, 0, 0,),  # black
)


def _update_cbars_with_max(color_depth):
    global COLOR_BARS

    cbars = [list(clr) for clr in COLOR_BARS]
    cbarvals = [None for _ in range(len(cbars))]
    color_max_val = [(2**w)-1 for w in color_depth]
    
    for cc in range(len(cbars)):
        for ii in range(3):
            if cbars[cc][ii] == 1:
                cbars[cc][ii] = color_max_val[ii]
        
        # create a single value out of pixel tuple, note list index 
        # the reverse diretion of bit-vectors (intbv) index.
        s1, s2 = sum(color_depth[1:]), color_depth[-1]
        val = (cbars[cc][0] << s1) + \
              (cbars[cc][1] << s2) + \
              cbars[cc][2]

        cbarvals[cc] = val

    cbarvals = tuple(cbarvals)
    print("Color bar values:")
    for ii in range(len(cbarvals)):
        print("   {:3d}:  {:08X}".format(ii, cbarvals[ii]))

    return cbarvals
    

@myhdl.block
def color_bars(glbl, vmem, resolution=(640, 480), color_depth=(10, 10, 10)):
    """ generate a color bar pattern
    """
    global COLOR_BARS

    pwidth = sum(color_depth)   # width of the pixel bit-vector
    num_colors, pmax, res = len(COLOR_BARS), (2**pwidth)-1, resolution

    cbarvals = _update_cbars_with_max(color_depth)

    # the width of each boundary (each bar)
    pw = int(res[0] // num_colors)
    
    clock, reset = glbl.clock, glbl.reset
    pixel = Signal(intbv(0)[pwidth:])
    ssel = Signal(intbv(0)[32:0])   # DEBUG

    # get the pixel value for the current pixel address,
    # only the horizontal pixel address is needed.
    @always_comb
    def beh_pval():
        sel = 0
        for ii in range(num_colors):
            if vmem.hpxl > (ii*pw):
                sel = ii
        ssel.next = sel
        pixel.next = cbarvals[sel]

    # get the slice of the pixel for each color
    cd = color_depth
    print("COLORBARS: ", pwidth, cd)
    red = pixel(pwidth, pwidth-cd[0])
    green = pixel(pwidth-cd[0], pwidth-cd[0]-cd[1])
    blue = pixel(pwidth-cd[0]-cd[1], 0)
    for width, slc in zip(color_depth, (red, green, blue)):
        assert width == len(slc)

    @always_seq(clock.posedge, reset=reset)
    def beh_rgb():
        # unpack the RGB value
        vmem.red.next = red
        vmem.green.next = green
        vmem.blue.next = blue

    return beh_pval, beh_rgb
