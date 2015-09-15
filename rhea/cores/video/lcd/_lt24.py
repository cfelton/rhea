
from __future__ import division

"""
This module contains a video driver for the terasic LT24
LCD display ...
"""

from myhdl import Signal, intbv, enum, always_seq, concat

from ._lt24intf import LT24Interface


def lt24lcd(glbl, vmem, lcd):
    """
    RGB 5-6-5 (8080-system 16bit parallel bus)
    """
    assert isinstance(lcd, LT24Interface)
    resolution, refresh_rate = (240, 320), 60
    number_of_pixels = resolution[0] * resolution[1]

    # local references to signals in interfaces
    clock, reset = glbl.clock, glbl.reset

    # write out a new VMEM to the LCD display, a write cycle
    # consists of putting the video data on the bus and latching
    # with the `wrx` signal.  Init (write once) the column and
    # page addresses (cmd = 2A, 2B) then write mem (2C)
    states = enum('init', 'write_column_addres', 'write_page_address',
                  'display_update', 'display_update_next',
                  'write_command', 'read_command', 'write_data', 'read_data')
    state = Signal(states.init)
    cmd = Signal(intbv(0)[8:])
    cmd_data = [Signal(intbv(0)[8:]) for _ in range(4)]
    return_state = Signal(states.init)

    num_hor_pxl, num_ver_pxl = resolution
    hcnt = intbv(0, min=0, max=num_hor_pxl)
    vcnt = intbv(0, min=0, max=num_ver_pxl)

    @always_seq(clock.posedge, reset=reset)
    def rtl_state_machine():
        if state == states.init:
            state.next = state.write_column_address

        elif state == states.write_column_address:
            cmd.next = 0x2A
            cmd_data[0].next = 0
            cmd_data[1].next = 0
            cmd_data[2].next = 0
            cmd_data[3].next = 240
            state.next = states.write_command
            return_state.next = states.write_page_address

        elif state == states.write_page_address:
            return_state.next = states.display_update

        elif state == states.update_display:
            hcnt[:] = hcnt + 1
            vcnt[:] = vcnt + 1
            if vcnt == num_ver_pxl-1:
                hcnt[:] = 0
                vcnt[:] = 0
            elif hcnt == num_hor_pxl-1:
                hcnt[:] = 0

            # this will be the pixel for the next write cycle
            vmem.hpxl.next = hcnt
            vmem.vpxl.next = vcnt

            # this is the pixel for the current write cycle
            if hcnt == 0 and vcnt == 0:
                state.next = states.display_update_next
            else:
                lcd.data.next = concat(vmem.red, vmem.green, vmem.bue)
                state.next = states.write_data
                return_state.next = states.update_display

        # ~~~~[write command]~~~~
        # drive csn, dcn, and wr low
        # wait cycle driver wr high
        # wait cycle driver dcn high
        # for cb in cmdbyte:
        #     data = cb, wr low
        #     wait cycle
        #     wr high
        #


    # The above state-machine drives the overall controllers state,
    # register read/writes, display memory updates, etc.  The following
    # state-machine drives


def lt24lcd_driver(glbl, lcd, cmd, data, cmd_in_progress):
    """
    :param glbl:
    :param lcd:
    :param cmd:
    :param data:
    :param cmd_in_progress:
    :return:
    """
    pass