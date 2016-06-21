
"""
This is an LT24 LCD driver example.
"""

from __future__ import division

import myhdl
from myhdl import (Signal, intbv, always_comb, always_seq,
                   always, TristateSignal, concat, instances)

from rhea.system import Global, Clock, Reset
from rhea.cores.video import VideoMemory
from rhea.cores.video import color_bars
from rhea.cores.video.lcd import lt24lcd
from rhea.cores.video.lcd import LT24Interface
from rhea.cores.misc import glbl_timer_ticks

import rhea.build as build
from rhea.build.boards import get_board

# board definition for the automated flow
brd, flow = None, None


@myhdl.block
def de0nano_lt24lcd(clock, reset, led,
    # LT24 LCD display signals
    lcd_on, lcd_resetn, lcd_csn, lcd_rs,
    lcd_wrn, lcd_rdn, lcd_data
):
    """    
    The port names are the same as those in the board definition
    (names in the user manual) for automatic mapping by the 
    rhea.build automation.
    """
    # signals and interfaces
    glbl = Global(clock, reset)

    # ----------------------------------------------------------------
    # global ticks
    tick_inst = glbl_timer_ticks(glbl, include_seconds=True, user_timer=16)

    heartbeat = Signal(bool(0))

    @always_seq(clock.posedge, reset=reset)
    def beh_leds():
        if glbl.tick_sec:
            heartbeat.next = not heartbeat
        led.next = concat(intbv(0)[7:], heartbeat)

    # ----------------------------------------------------------------
    # LCD dislay
    lcd = LT24Interface()    
    resolution, color_depth = lcd.resolution, lcd.color_depth
    lcd.assign(
        lcd_on, lcd_resetn, lcd_csn, lcd_rs, lcd_wrn, lcd_rdn, lcd_data
    )

    # color bars and the interface between video source-n-sink
    vmem = VideoMemory(resolution=resolution, color_depth=color_depth)
    bar_inst = color_bars(glbl, vmem, resolution=resolution, color_depth=color_depth)

    # LCD video driver
    lcd_inst = lt24lcd(glbl, vmem, lcd)

    return myhdl.instances()


# the default port map
# @todo: should be able to extact this from the board
#        definition:
#        portmap = brd.map_ports(de0nano_converters)
de0nano_lt24lcd.portmap = {
    'clock': Clock(0, frequency=50e6),
    'reset': Reset(0, active=0, async=True),
    'led': Signal(intbv(0)[8:]),
    'lcd_on': Signal(bool(1)),
    'lcd_resetn': Signal(bool(1)),
    'lcd_csn': Signal(bool(1)),
    'lcd_rs': Signal(bool(1)),
    'lcd_wrn': Signal(bool(1)),
    'lcd_rdn': Signal(bool(1)),
    'lcd_data': Signal(intbv(0)[16:])
}


def build():
    global brd, flow
    brd = get_board('de0nano')
    flow = brd.get_flow(top=de0nano_lt24lcd)
    flow.run()

    
def program():
    if flow is not None:
        flow.program()


if __name__ == '__main__':
    build()
    program()
