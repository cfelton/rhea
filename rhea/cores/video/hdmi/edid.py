
from __future__ import division

from datetime import datetime
from myhdl import intbv, modbv

HEADER = (0x00, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x00)


class ExtendedDisplayIDData(object):
    """
    Extended Display Identification Data (EDID)

    Fields (object attributes) defined in the EEDIDrAr2.pdf
    and can be found here: http://www.drhdmi.eu/dictionary/edid.html
    """
    def __init__(self, resolution=(640, 480,), refresh_rate=60,
                 aspect=(16,9) ):
        """
        """
        # vendor and product identification
        self._mfg_name = 'ABC'
        self._pid = intbv(0x72)[16:]
        self._serial_number = intbv(1)[32:]
        self._mfg_date = datetime.today()
        self._mfg_week = self._mfg_date.isocalendar()[1]
        self._mfg_year = self._mfg_date.year - 1990
        # EDID structure (version.revision)
        self._version = '1.4'   
        # basic display info (section 3.6)        
        self._display_type = 'hdmi-a'
        self._color_depth = 8
        self._refresh_rate = refresh_rate
        self._resolution = resolution
        self._horizontal_size = resolution[0]
        self._vertical_size = resolution[1]
        self._aspect = aspect
        self._landscape = True if aspect[0] > aspect[1] else False
        self._aspect_ratio = aspect[0] / aspect[1]
        self._gamma = 2.2

        # example of an x,y chroma table
        # 655 (28F) --> 0.6396484375
        # 338 (152) --> 0.330078125
        # 307 (133) --> 0.2998046875
        # 614 (266) --> 0.599609375
        # 154 (09A) --> 0.150390625
        # 61  (03D) --> 0.0595703125
        # 320 (140) --> 0.3125
        # 337 (151) --> 0.3291015625
        # @todo: add binary fracction conversion and used 
        # @todo: use decimal fractions in xy_chroma table
        self._xy_chroma = (655, 338, 307, 614, 154, 61, 320, 337)

        # @todo: color characteristics (section 3.7)

        # @todo: timing ... (section 3.8 and 3.9)
        
        self._rom = [intbv(0)[8:] for _ in range(128)]

    def __str__(self):
        txt = "\n"
        skiplist = ['_header', '_rom']
        for k, v in self.__dict__.items():
            if k in skiplist:
                continue
            key = k if '_' != k[0] else k[1:]
            ndots = 24-len(key)
            assert ndots > 0
            val = int(v) if isinstance(v, intbv) else v
            txt += "  {} {} {:<15} \n".format(key, '.'*ndots, str(val))
        return txt

    @property
    def version(self):
        return self._version

    @version.setter
    def version(self, val):
        ver = float(val)
        assert ver in (1.3, 1.4)
        self._version = val
        
    def get_rom_text(self):
        nrows, txt = 128//16, ''
        rom = self._rom
        # print(nrows*16)
        rowstr = "{:3d}:"+" {:02X} "*16
        # print(type(rowstr), rowstr)
        for ii in range(nrows):
            # print(ii*16, *(rom[ii*16:ii*16+16]))
            txt += rowstr.format(ii*16, *(map(int, rom[ii*16:ii*16+16]))) 
            txt += "\n"
            # print(txt)
        return txt

    def build_rom(self):
        """
        setup the default EDID fields, see table 3.1 in the VESA
        standard: "VESA Enhanced EDID Standard, Release A, REv.2"
        """
        rom = self._rom    

        # header at offset 00h
        self._header = HEADER   # 00h 
        for ii, bb in enumerate(HEADER):
            rom[ii] = intbv(bb)[8:]

        # Vendor & Product Indentification
        # the three character ISE ID code uses compressed ASCII, 
        # a complete table would need to be generated, only created
        # the values used.
        chars = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
        keyvalue = list(zip(chars, list(range(1, len(chars)+1)) ))
        ascii_5bitmap = dict(keyvalue)
        mfgname = intbv(0)[15:]
        mfgname[15:10] = ascii_5bitmap[self._mfg_name[0]]
        mfgname[10:5] = ascii_5bitmap[self._mfg_name[1]]
        mfgname[5:0] = ascii_5bitmap[self._mfg_name[2]]
        rom[0x08] = mfgname[16:8]
        rom[0x09] = mfgname[8:0]

        rom[0x0A] = self._pid[8:0]
        rom[0x0B] = self._pid[16:8]

        rom[0x0C] = self._serial_number[8:0]
        rom[0x0D] = self._serial_number[16:8]
        rom[0x0E] = self._serial_number[24:16]
        rom[0x0F] = self._serial_number[32:24]
        
        # EDID Structure Version & Revision
        rom[0x12] = int(self._version.split('.')[0])
        rom[0x13] = int(self._version.split('.')[1])

        # Basic Display Parameters & Features

        # video input 14h
        b = intbv(0)[8:]
        b[7] = 1          # always digital :)
        color_depth_map = {6: 1, 8: 2, 10:3, 12: 4,
                           14: 5, 16:6}
        b[7:4] = color_depth_map[self._color_depth]  
        interface_standard_map = {'dvi': 1, 'hdmi-a':2,
                                  'hdmi-b':3, 'mddi':4,
                                  'displayport':5}
        b[4:0] = interface_standard_map[self._display_type.lower()]
        rom[0x14] = b

        if self._landscape:
            rom[0x15] = int(round((100 * self._aspect_ratio) - 99))
            rom[0x16] = 0
        else:
            rom[0x15] = int(round((100 / self._aspect_ratio) - 99))
            rom[0x16] = 0

        rom[0x17] = int(round((self._gamma * 100) - 100))

        # @todo: determine if not preferred timing mode ...
        rom[0x18] = intbv('000_01_11_110')[8:0]
        #                  |   |  |  +++- standard and preferred
        #                  |   |  +------ RGB 4:4: & YCrCb 4:4:4 & YCrCb 4:2:2        
        #                  |   +--------- RGB color display
        #                  +------------- no power management

        # x,y chroma table 
        rgbwlsbits = intbv(0)[16:]
        for ii, xy in enumerate(self._xy_chroma):
            val = intbv(xy)[10:]
            rom[0x1B+ii] = val[10:2]
            rgbwlsbits[16-2*ii:16-2*ii-2] = val[2:0]

        rom[0x19] = rgbwlsbits[16:8]
        rom[0x1A] = rgbwlsbits[8:0]

        # Color Characteristics

        # Established Timings
        # The established timings is optional in 1.4, this can be 
        # used to indicated compability with certain video modes.
        timings = intbv(0)[24:]
        timing_bit_map = {
            # most significant bits, 0x25
            (1152, 870, 75): 16, 
            # middle bits, 0x24
            (800, 600, 72): 15, (800, 600, 75): 14, (832, 624, 75): 13,
            (1024, 768, 87): 12, (1024, 768, 60): 11, (1024, 768, 70): 10,
            (1024, 768, 75): 9, (1280, 1024, 75): 8,
            # least significant bits, 0x23
            (720, 400, 70): 7, (720, 400, 80): 6, (640, 480, 60): 5,
            (640, 480, 67): 4, (640, 480, 72): 3, (640, 480, 75): 2,
            (800, 600, 56): 1, (800, 600, 60): 0,                          
        }
        timing_key = self._resolution + (self._refresh_rate,)
        bit_select = timing_bit_map[timing_key]
        timings[bit_select] = 1
        rom[0x23] = timings[8:0]
        rom[0x24] = timings[16:8]
        rom[0x25] = timings[24:16]

        # Standard Timings: (Id 1-8)
        # The use of the standard timings is options, these provide
        # indentification for upto 8 additiona timings.  Use the 
        # StandardTiming object to create the two byte needed for
        # each entry
        for ii in range(0, 16,2):
            rom[0x26+ii:0x26+ii+2] = StandardTimings().get_empty()
            # example setting standard timing
            # rom[0x26+ii:0x26+ii+2] = StandardTimings(
            #                             resolution=(1920, 1080),
            #                             refresh_rate=75,
            #                             aspect=(16, 9).get_bytes()

        # 18 Byte Data Blocks

        # Checksum
        checksum = modbv(0)[8:]
        for ii in range(len(rom)-1):
            checksum[:] = checksum + int(rom[ii])
        rom[0x7F] = checksum

        assert None not in rom
        # mare sure all are intbv (range checking)
        for ii, v in enumerate(rom):
            if isinstance(v, intbv):
                rom[ii] = v
            else:
                rom[ii] = intbv(v)[8:]

        return rom

    def extract_rom(self, rom):
        # @todo: complete
        self.header = tuple(map(int, rom[0:8]))


class StandardTimings(object):
    def __init__(self, resolution=(1080, 1024), aspect=(16,9), refresh_rate=60):
        """
        16 byte standard timing information
        """
        b0 = intbv(0)[8:]
        b0[:] = (resolution[0]//8) - 31
        self._horzaddr = b0
        image_aspect_ratio_map = {(16, 10): 0, (4, 3): 1, 
                                  (5, 4): 2, (16, 9): 3}
        b1 = intbv(0)[8:]
        b1[8:6] = image_aspect_ratio_map[aspect]
        b1[6:0] = refresh_rate - 60
        self._bytes = [b0, b1]

    def get_bytes(self):
        return self._bytes

    def get_empty(self):
        return [0x01, 0x10]


class DetailedTimings(object):
    def __init__(self, name="", ):
        """
        The 
        """
        self._name = name
        self._pixel_clock = 0 

    def get_bytes(self):
        pass


class DisplayDescriptor(object):
    def __init__(self, name=""):
        """
        """
        self._name = name

    def get_bytes(self):
        pass