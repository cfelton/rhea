
from __future__ import division

"""
This module contains a video driver for the terasic LT24
LCD display ...
"""

from myhdl import Signal, intbv, enum, always_seq, concat

from ._lt24intf import LT24Interface


# the following table defines the LCD init squence,
# the sequency will be formatted into a ROM
#   00: cmd length  (total length)
#   01  pause, delay in milliseconds
#   01: cmd
#   02: cmd data[0]
#   ...

init_sequence = {
    0x11: dict(data=[], pause=120),   # 
    0xCF: dict(data=[0x00, 0x83, 0x30], pause=0),
    0xED: dict(data=[0x64, 0x03, 0x12, 0x81], pause=0),
    0xE8: dict(data=[0x85, 0x00, 0x78], pause=0),
    0xCB: dict(data=[0x39, 0x2C, 0x00, 0x34, 0x02], pause=0),
    0xF7: dict(data=[0x20], pause=0),
    0xEA: dict(data=[0x00, 0x00], pause=0),
    0xC0: dict(data=[0x19], pause=0),
    0xC1: dict(data=[0x11], pause=0),
    0xC5: dict(data=[0x3C, 0x3F], pause=0),
    0xC7: dict(data=[0x90], pause=0),
    0x36: dict(data=[0x28], pause=0),
    0x3A: dict(data=[0x55], pause=0),
    0xB1: dict(data=[0x00, 0x17], pause=0),
    0xB6: dict(data=[0x0A, 0xA2], pause=0),
    0xF6: dict(data=[0x01, 0x30], pause=0),
    0xF2: dict(data=[0x00], pause=0),    
    0x2A: dict(data=[0x00, 0x00, 0x00, 0xEF], pause=0),
    0x2B: dict(data=[0x00, 0x00, 0x01, 0x40], pause=0),
    0x11: dict(data=[], pause=120),
    0x29: dict(data=[], pause=30),    # 
}


def build_init_rom(init_sequence):
    mem, maxpause = [], 0
    for cmd, info in init_sequence.items():
        cmd_entry = [len(info['data'])+3] + [info['pause']] + \
                    [cmd] + info['data']
        print(cmd_entry)
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

    # write out a new VMEM to the LCD display, a write cycle
    # consists of putting the video data on the bus and latching
    # with the `wrx` signal.  Init (write once) the column and
    # page addresses (cmd = 2A, 2B) then write mem (2C)
    states = enum(
        'init_wait_reset',
        'init_start',
        'init_start_cmd', 
        'init_next',

        'write_cmd_start',
        'write_cmd',

        'display_update_start',
        'display_update',
        'display_update_next',
        'display_update_end'
    )

    state = Signal(states.init_wait_reset)
    cmd = Signal(intbv(0)[8:])
    cmddata = [Signal(intbv(0)[8:]) for _ in range(4)]
    return_state = Signal(states.init_wait_reset)

    num_hor_pxl, num_ver_pxl = resolution
    hcnt = intbv(0, min=0, max=num_hor_pxl)
    vcnt = intbv(0, min=0, max=num_ver_pxl)

    # signals to start a new command transaction to the LCD
    datalen = Signal(intbv(0, min=0, max=number_of_pixels+1))
    data = Signal(intbv(0)[16:])
    datasent = Signal(bool(0))
    cmd_in_progress = Signal(bool(0))

    # --------------------------------------------------------
    # LCD driver
    gdrv = lt24lcd_driver(glbl, lcd, cmd, datalen, data,
                          datasent, cmd_in_progress)

    rom, romlen, maxpause = build_init_rom(init_sequence)
    offset = Signal(intbv(0, min=0, max=romlen))
    pause = Signal(intbv(0, min=0, max=maxpause))

    @always_seq(clock.posedge, reset=reset)
    def rtl_state_machine():

        if state == states.init_wait_reset:
            if lcd.reset_complete:
                state.next = states.init_start

        elif state == states.init_start:
            v = rom[offset]
            #cmdlen.next = v
            datalen.next =  v - 3
            p = rom[offset+1]
            pause.next = p
            offset.next = offset + 2
            state.next = states.init_start_cmd

        elif state == states.init_start_cmd:
            v = rom[offset]
            cmd.next = v
            offset.next = offset + 1
            state.next = states.write_cmd_start
            return_state.next = states.init_next

        elif state == states.init_next:
            if glbl.tick_ms:
                if pause == 0:
                    if offset == romlen-1:
                        state.next = states.display_update_start
                    else:
                        state.next = states.init_start
                else:
                    pause.next = pause - 1

        elif state == states.write_cmd_start:
            state.next = states.write_cmd

        elif state == states.write_cmd:
            if cmd_in_progress:
                if datasent:
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
            xfercnt.next = 2
            lcd.reset_complete.next = False
            state.next = states.reset

        elif state == states.reset:
            if glbl.tick_ms:
                if xfercnt == 0:
                    lcd.resetn.next = False
                    xfercnt.next = 10
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
