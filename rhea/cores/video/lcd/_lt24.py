
from __future__ import division

"""
This module contains a video driver for the terasic LT24
LCD display ...
"""
from myhdl import Signal, intbv, enum, always_seq, concat

from ._lt24intf import LT24Interface


# the following table defines the LCD init sequence,
# the sequence will be formatted into a ROM
#   00: cmd length  (total length)
#   01  pause, delay in milliseconds
#   01: cmd
#   02: cmd data[0]
#   ...
# init sequence from http://www.avrfreaks.net/sites/default/files/ILI9341.c
seq = []
seq += [dict(cmd=0x11, data=[], pause=120)]
seq += [dict(cmd=0xCF, data=[0x00, 0x83, 0x30], pause=0)]
seq += [dict(cmd=0xED, data=[0x64, 0x03, 0x12, 0x81], pause=0)]
seq += [dict(cmd=0xE8, data=[0x85, 0x00, 0x78], pause=0)]
seq += [dict(cmd=0xCB, data=[0x39, 0x2C, 0x00, 0x34, 0x02], pause=0)]
seq += [dict(cmd=0xF7, data=[0x20], pause=0)]
seq += [dict(cmd=0xEA, data=[0x00, 0x00], pause=0)]
seq += [dict(cmd=0xC0, data=[0x19], pause=0)]
seq += [dict(cmd=0xC1, data=[0x11], pause=0)]
seq += [dict(cmd=0xC5, data=[0x3C, 0x3F], pause=0)]
seq += [dict(cmd=0xC7, data=[0x90], pause=0)]
seq += [dict(cmd=0x36, data=[0x28], pause=0)]
seq += [dict(cmd=0x3A, data=[0x55], pause=0)]
seq += [dict(cmd=0xB1, data=[0x00, 0x17], pause=0)]
seq += [dict(cmd=0xB6, data=[0x0A, 0xA2], pause=0)]
seq += [dict(cmd=0xF6, data=[0x01, 0x30], pause=0)]
seq += [dict(cmd=0xF2, data=[0x00], pause=0)]
seq += [dict(cmd=0x11, data=[], pause=120)]
seq += [dict(cmd=0x29, data=[], pause=30)]
seq += [dict(cmd=0x2A, data=[0x00, 0x00, 0x00, 0xEF], pause=0)]
seq += [dict(cmd=0x2B, data=[0x00, 0x00, 0x01, 0x40], pause=0)]
init_sequence = seq


def build_init_rom(init_sequence):
    mem, maxpause = [], 0
    for info in init_sequence:
        assert isinstance(info, dict)
        cmd_entry = [len(info['data'])+3] + [info['pause']] + \
                    [info['cmd']] + info['data']
        print("{cmd:02X} {pause} {data} {bb}".format(
              bb=list(map(hex, cmd_entry)), **info))
        maxpause = max(maxpause, info['pause'])
        mem = mem + cmd_entry
    rom = tuple(mem)
    return rom, len(rom), maxpause


def lt24lcd(glbl, vmem, lcd):
    """
    RGB 5-6-5 (8080-system 16bit parallel bus)
    """
    assert isinstance(lcd, LT24Interface)
    resolution, refresh_rate = (240, 320), 60
    number_of_pixels = resolution[0] * resolution[1]

    # local references to signals in interfaces
    clock, reset = glbl.clock, glbl.reset

    # make sure the user timer is configured
    assert glbl.tick_user is not None

    # write out a new VMEM to the LCD display, a write cycle
    # consists of putting the video data on the bus and latching
    # with the `wrx` signal.  Init (write once) the column and
    # page addresses (cmd = 2A, 2B) then write mem (2C)
    states = enum(
        'init_wait_reset',      # wait for the controller to reset the LCD
        'init_start',           # start the display init sequence
        'init_start_cmd',       # send a command, port of the display seq
        'init_next',            # determine if another command

        'write_cmd_start',       # command subroutine
        'write_cmd',             # command subroutine

        'display_update_start',  # update the display
        'display_update',
        'display_update_next',
        'display_update_end'
    )

    state = Signal(states.init_wait_reset)
    cmd = Signal(intbv(0)[8:])
    return_state = Signal(states.init_wait_reset)

    num_hor_pxl, num_ver_pxl = resolution
    hcnt = intbv(0, min=0, max=num_hor_pxl)
    vcnt = intbv(0, min=0, max=num_ver_pxl)

    # signals to start a new command transaction to the LCD
    datalen = Signal(intbv(0, min=0, max=number_of_pixels+1))
    data = Signal(intbv(0)[16:])
    datasent = Signal(bool(0))
    datalast = Signal(bool(0))
    cmd_in_progress = Signal(bool(0))

    # --------------------------------------------------------
    # LCD driver
    gdrv = lt24lcd_driver(glbl, lcd, cmd, datalen, data,
                          datasent, datalast, cmd_in_progress)

    # --------------------------------------------------------
    # build the display init sequency ROM
    rom, romlen, maxpause = build_init_rom(init_sequence)
    offset = Signal(intbv(0, min=0, max=romlen+1))
    pause = Signal(intbv(0, min=0, max=maxpause+1))

    # --------------------------------------------------------
    # state-machine

    @always_seq(clock.posedge, reset=reset)
    def rtl_state_machine():

        if state == states.init_wait_reset:
            if lcd.reset_complete:
                state.next = states.init_start

        elif state == states.init_start:
            v = rom[offset]
            # @todo: change the table to only contain the number of
            # @todo: bytes to be transferred
            datalen.next = v - 3
            p = rom[offset+1]
            pause.next = p
            offset.next = offset + 2
            state.next = states.init_start_cmd

        elif state == states.init_start_cmd:
            v = rom[offset]
            cmd.next = v
            if datalen > 0:
                v = rom[offset+1]
                data.next = v
                offset.next = offset + 2
            else:
                offset.next = offset + 1
            state.next = states.write_cmd_start
            return_state.next = states.init_next

        elif state == states.init_next:
            if pause == 0:
                if offset == romlen:
                    state.next = states.display_update_start
                else:
                    state.next = states.init_start
            elif glbl.tick_ms:
                    pause.next = pause - 1

        elif state == states.write_cmd_start:
            state.next = states.write_cmd

        elif state == states.write_cmd:
            if cmd_in_progress:
                if datasent and not datalast:
                    v = rom[offset]
                    data.next = v
                    offset.next = offset+1
            else:
                cmd.next = 0
                state.next = return_state

        elif state == states.display_update_start:
            if glbl.tick_user:
                cmd.next = 0x2C
                state.next = states.display_update
                datalen.next = number_of_pixels

        elif state == states.display_update:
            hcnt[:] = hcnt + 1
            if vcnt == num_ver_pxl-1:
                hcnt[:] = 0
                vcnt[:] = 0
            elif hcnt == num_hor_pxl-1:
                hcnt[:] = 0
                vcnt[:] = vcnt + 1

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
                if datasent and not datalast:
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
                   datasent, datalast, cmd_in_progress, maxlen=76800):
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

    states = enum(
        'reset_start',
        'reset',
        'reset_wait',
        'wait', 
        'write_command_start', 
        'write_command_data', 
        'write_command_xsetup', 
        'write_command_xlatch',
        'end'
    )

    state = Signal(states.reset_start)
    xfercnt = Signal(intbv(0, min=0, max=maxlen+1))
    lcd.reset_complete = Signal(bool(0))

    @always_seq(clock.posedge, reset=reset)
    def rtl_state_machine():

        if state == states.reset_start:
            lcd.resetn.next = True
            lcd.csn.next = True
            lcd.wrn.next = True
            lcd.rdn.next = True
            lcd.dcn.next = True        
            lcd.on.next = True
            xfercnt.next = 2  # used as ms counter
            lcd.reset_complete.next = False
            state.next = states.reset

        elif state == states.reset:
            if glbl.tick_ms:
                if xfercnt == 0:
                    lcd.resetn.next = False
                    xfercnt.next = 10  # used as ms counter
                    state.next = states.reset_wait
                else:
                    xfercnt.next = xfercnt - 1

        elif state == states.reset_wait:
            if glbl.tick_ms:
                if xfercnt == 0:
                    lcd.resetn.next = True
                    state.next = states.wait
                    lcd.reset_complete.next = True
                else:
                    xfercnt.next = xfercnt - 1

        # wait for a new command
        elif state == states.wait:
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
                lcd.csn.next = True
                lcd.wrn.next = True
                lcd.rdn.next = True
                lcd.dcn.next = True                
                
        # start a write command
        elif state == states.write_command_start:
            lcd.wrn.next = True
            state.next = states.write_command_data

        # setup the data portion of the command
        elif state == states.write_command_data:
            lcd.dcn.next = True
            xfercnt.next = 0
            if datalen == 0:
                lcd.wrn.next = True
                state.next = states.end
            else:
                lcd.wrn.next = False
                state.next = states.write_command_xsetup

        # transfer the data setup
        elif state == states.write_command_xsetup:
            lcd.wrn.next = False
            lcd.data.next = data 
            datasent.next = True
            if xfercnt == datalen-1:
                datalast.next = True
            xfercnt.next = xfercnt + 1
            state.next = states.write_command_xlatch

        # transfer the data latch
        elif state == states.write_command_xlatch:
            lcd.wrn.next = True
            datasent.next = False
            datalast.next = False
            if xfercnt == datalen:
                state.next = states.end
            else:
                state.next = states.write_command_xsetup

        # end of the transaction
        elif state == states.end:
            lcd.csn.next = True
            cmd_in_progress.next = False
            if cmd == 0:
                state.next = states.wait
                
        else:
            assert False, "Invalid state %s" % (state,)
            
    return rtl_state_machine
