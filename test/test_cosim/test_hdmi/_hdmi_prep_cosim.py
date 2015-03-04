
import os

from myhdl import *
#from _hdmi_ref_filelist import filelist
filist = []

def prep_cosim(
        clock,
        reset,
        hdmi_src=None,
        hdmi_snk=None,
        args=None):
    """
    """
    global filelist
    files = filelist + ['tb_hdmi.v']
    print("compiling")
    cmd = "iverilog -o hdmi -y xsim %s " % (" ".join(files),)
    os.system(cmd)

    if not os.path.exists('vcd'):
        os.makedirs('vcd')

    print("cosimulation setup ...")
    cmd = "vvp -m ./myhdl.vpi hdmi"
    
    gcosim = Cosimulation(
        cmd,
        clock=clock,
        reset_n=reset,
        # HDMI ports
    )

    return gcosim