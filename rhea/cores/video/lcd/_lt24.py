
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
    states = enum('init',
                  'write_column_address',
                  'write_page_address',
                  'write_wait_pre',
                  'write_wait',
                  'display_update_start',
                  'display_update',
                  'display_update_next',
                  'display_update_end')
    state = Signal(states.init)
    cmd = Signal(intbv(0)[8:])
    cmddata = [Signal(intbv(0)[8:]) for _ in range(4)]
    return_state = Signal(states.init)

    num_hor_pxl, num_ver_pxl = resolution
    hcnt = intbv(0, min=0, max=num_hor_pxl)
    vcnt = intbv(0, min=0, max=num_ver_pxl)
    cindx = intbv(0, min=0, max=number_of_pixels+1)
    csig = Signal(cindx)

    datalen = Signal(intbv(0, min=0, max=number_of_pixels+1))
    data = Signal(intbv(0)[16:])
    datasent = Signal(bool(0))
    cmd_in_progress = Signal(bool(0))

    gdrv = lt24lcd_driver(glbl, lcd, cmd, datalen, data,
                          datasent, cmd_in_progress)

    @always_seq(clock.posedge, reset=reset)
    def rtl_state_machine():
        if state == states.init:
            cindx[:] = 0
            state.next = states.write_column_address

        elif state == states.write_column_address:
            cmd.next = 0x2A
            cmddata[0].next = 0     # start address MSB
            cmddata[1].next = 0     # start address LSB
            cmddata[2].next = 0     # end address MSB
            cmddata[3].next = 0xEF  # end address LSB
            cindx[:] = 0
            data.next = cmddata[cindx]
            datalen.next = 4
            state.next = states.write_wait_pre
            return_state.next = states.write_page_address

        elif state == states.write_page_address:
            cmd.next = 0x2B
            cmddata[0].next = 0     # start address MSB
            cmddata[1].next = 0     # start address LSB
            cmddata[2].next = 0x01  # end address MSB
            cmddata[3].next = 0x40  # end address LSB
            cindx[:] = 0
            data.next = cmddata[cindx]
            datalen.next = 4
            state.next = states.write_wait_pre
            return_state.next = states.display_update_start

        elif state == states.write_wait_pre:
            state.next = states.write_wait

        elif state == states.write_wait:
            csig.next = cindx
            if cmd_in_progress:
                if datasent:
                    cindx[:] = cindx + 1
                    if cindx < datalen:
                        data.next = cmddata[cindx]
            else:
                cmd.next = 0
                state.next = return_state

        elif state == states.display_update_start:
            cmd.next = 0x2C
            state.next = states.display_update
            datalen.next = number_of_pixels

        elif state == states.display_update:
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
                state.next = states.display_update_end
            else:
                data.next = concat(vmem.red, vmem.green, vmem.blue)
                state.next = states.display_update_next

        elif state == states.display_update_next:
            if cmd_in_progress:
                if datasent:
                    state.next = states.display_update
            else:
                cmd.next = 0
                state.next = states.display_update_end

        elif state == states.display_update_end:
            # @todo: wait for next update
            if not cmd_in_progress:
                state.next = states.display_update

    return gdrv, rtl_state_machine


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
    xfercnt = Signal(intbv(0, min=0, max=maxlen+1))
    
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

        # setup the data portion of the command
        elif state == states.write_command_data:
            lcd.dcn.next = True 
            lcd.wrn.next = False
            xfercnt.next = 0
            state.next = states.write_command_xsetup

        # transfer the data setup
        elif state == states.write_command_xsetup:
            lcd.wrn.next = False
            lcd.data.next = data 
            datasent.next = True
            xfercnt.next = xfercnt + 1
            state.next = states.write_command_xlatch

        # transfer the data latch
        elif state == states.write_command_xlatch:
            lcd.wrn.next = True
            datasent.next = False
            if xfercnt == datalen:
                state.next = states.end
            else:
                state.next = states.write_command_xsetup

        # end of the transaction
        elif state == states.end:
            cmd_in_progress.next = False
            if cmd == 0:
                state.next = states.wait
                
        else:
            assert False, "Invalid state %s" % (state,)
            
    return rtl_state_machine
