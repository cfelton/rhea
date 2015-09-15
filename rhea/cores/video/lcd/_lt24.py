
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


def lt24lcd_driver(glbl, lcd, cmd, datalen, data, 
                   datasent, cmd_in_progress, maxlen=76800):
    """
    :param glbl:
    :param lcd:
    :param cmd: 
    :param datalen: number of data xfer to do
    :param data: data to be sent
    :param data_sent: one cycle strobe indicating the data xfered
    :param cmd_in_progress:
    :return:
    
    Typical confgiruration write
       clock:             /--\__/--\__/--\__/--\__/--\__/--\__/--\__
       cmd:               0x00    | 0x2B 
       cmd_in_progress:   ____________/----------------
                                            ^ cmd latched
                                                  ^ first data byte for command
       datasent           ________________________/----\_____
       
    The transaction is started by setting the `cmd` signal to nonzero,
    the command byte is transferred and then the frist data, when then
    first data is transferred the `datasent` is strobe, this indicates 
    to the source (producer) to update `data` to the next value. 
    The `cmd` must go to zero before the next transfer can occur. 
    
    Future enhancements:
    @todo: add read commands 
    """
    
    # local references
    clock, reset = glbl.clock, glbl.reset 
    
    states = enum('wait', 
                  'write_command_start', 
                  'write_command_data', 
                  'write_command_xsetup', 
                  'write_command_xlatch',
                  'end')
    state = Signal(states.wait)
    xfercnt = Signal(intbv(0, min=0, max=maxlen))
    
    @always_seq(clock.posedge, reset=reset)
    def rtl_state_machine():
        
        # wait for a new command 
        if state == states.wait:
            datasent.next = False
            if cmd != 0x00:
                lcd.csn.next = False
                lcd.wrn.next = False
                lcd.dcn.next = False
                lcd.data.next = cmd 
                state.next = states.write_command_start
                cmd_in_progress.next = True
            else:
                cmd_in_progress.next = False
                
        # start a write command`
        elif state == states.write_command_start:
            lcd.wrn.next = True
            state.next = states.write_command_data
            
        elif state == states.write_command_data:
            lcd.dcn.next = True 
            lcd.wrn.next = False
            xfercnt.next = 0
            state.next = states.write_command_xsetup
            
        elif state == states.write_command_xsetup:
            lcd.wrn.next = False
            lcd.data.next = data 
            datasent.next = True
            xfercnt.next = xfercnt + 1
            state.next = states.write_command_xlatch
            
        elif state == states.write_command_xlatch:
            lcd.wrn.next = True
            datasent.next = False
            if xfercnt == datalen:
                state.next = states.end
            else:
                state.next = states.write_command_xsetup
                
        elif state == states.end:
            cmd_in_progress.next = False
            if cmd == 0:
                state.next = states.start
                
        else:
            assert False, "Invalid state %s" % (state)
            
    return rtl_state_machine
                