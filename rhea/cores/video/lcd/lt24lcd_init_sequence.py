

"""
The following describes the display initialization sequence.  This
init sequence was adapted from the display init sequence provided 
in the terasic example ILI9341.c

Refer to the ILI9341 datasheet for more information.


Init sequence overview
----------------------

   0x11: (section 8.2.12) turn off sleep mode, the datasheet indicates
         a delay of 5 msecs before next command and 120ms before this
         command can be sent if in sleep mode (0x10).

   0xCF: (8.4.2) Power control B, DC enable

   0xED: (8.4.6) Power on sequence control

   0xE8: (8.4.3) Driver timing control A

   0xCB: (8.4.1) Power control A

   0xF7: (8.4.8) Pump ratio control

   0xEA: (8.4.5) Driver timing control B

   0xC0


The display sequence will be converted into a ROM, the sequence 
ROM is organized as:
    00: data length (legth of the data bytes to send)
    01: pause, delay in ms after the command
    02: command to send
    03: command first data byte
    ...
    0cn: last command byte
    ...
    0n: last command  
"""

# init sequence from terasic uP code
# @todo: only a couple pauses, remove them from the sequence
#        save space in the ROM
seq = []
seq += [dict(cmd=0x00,
             data=[], pause=120)]
seq += [dict(cmd=0x11,
             data=[], pause=5)]
seq += [dict(cmd=0xCF,
             data=[0x00, 0x81, 0xC0], pause=0)]
seq += [dict(cmd=0xED,
             data=[0x64, 0x03, 0x12, 0x81], pause=0)]
seq += [dict(cmd=0xE8,
             data=[0x85, 0x00, 0x78], pause=0)]
seq += [dict(cmd=0xCB,
             data=[0x39, 0x2C, 0x00, 0x34, 0x02], pause=0)]
seq += [dict(cmd=0xF7,
             data=[0x20], pause=0)]
seq += [dict(cmd=0xEA,
             data=[0x00, 0x00], pause=0)]
seq += [dict(cmd=0xB1,
             data=[0x00, 0x1B], pause=0)]
seq += [dict(cmd=0xB6,
             data=[0x0A, 0xA2], pause=0)]
seq += [dict(cmd=0xC0,    # power control
             data=[0x05], pause=0)]
seq += [dict(cmd=0xC1,    # power control
             data=[0x11], pause=0)]
seq += [dict(cmd=0xC5,    # VCM control
             data=[0x45, 0x45], pause=0)]
seq += [dict(cmd=0xC7,    # VCM control 2
             data=[0xA2], pause=0)]
seq += [dict(cmd=0x36,    # memory access controll
             data=[0x08], pause=0)]
seq += [dict(cmd=0xF2,    # 3gamma functin diable
             data=[0x00], pause=0)]
seq += [dict(cmd=0x26,    # gamma set
             data=[0x01, 0x30], pause=0)]

seq += [dict(cmd=0xE0,    # set gamma table
             data=[0x0F, 0x26, 0x24, 0x0B, 0x0E, 0x08,
                   0x4B, 0xA8, 0x3B, 0x0A, 0x14, 0x06,
                   0x10, 0x09, 0x00], pause=0)]
seq += [dict(cmd=0xE1,    # set gamma table
             data=[0x00, 0x1C, 0x20, 0x04, 0x10, 0x08,
                   0x34, 0x47, 0x44, 0x05, 0x0B, 0x09,
                   0x2F, 0x36, 0x0F], pause=0)]
             
seq += [dict(cmd=0x2A, data=[0x00, 0x00, 0x00, 0xEF], pause=0)]
seq += [dict(cmd=0x2B, data=[0x00, 0x00, 0x01, 0x3F], pause=0)]
seq += [dict(cmd=0x3A, data=[0x55], pause=30)]
seq += [dict(cmd=0xF6, data=[0x01, 0x30, 0x00], pause=0)]
seq += [dict(cmd=0x29, data=[], pause=30)]  # display on
seq += [dict(cmd=0x2C, data=[], pause=30)] 
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
