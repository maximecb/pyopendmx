import time
import math
from pyftdi.ftdi import Ftdi

class DMXUniverse:
    def __init__(self, url='ftdi://ftdi:232:AL6E8JFW/1'):
        self.url = url

        self.port = Ftdi.create_from_url(url)
        self.port.reset()
        self.port.set_baudrate(baudrate=250000)
        self.port.set_line_property(bits=8, stopbit=2, parity='N', break_=False)
        assert self.port.is_connected

        # The 0th byte must be 0 (start code)
        # 513 bytes are sent in total
        self.data = bytearray(513 * [0])

    def __del__():
        self.port.close()

    def __setitem__(self, idx, val):
        assert (idx > 0)
        assert (idx <= 512)
        assert isinstance(val, int)
        assert (val >= 0 and val <= 255)
        self.data[idx] = val

    def update():
        """
        Write channel data to the output port
        """

        port.set_break(True)
        port.set_break(False)
        port.write_data(selfdata)

        time.sleep(20/1000.0)

class DMXDevice:
    def __init__(self, chan_no, num_chans):
        self.chan_no = chan_no
        self.num_chans = num_chans

    def update(self, dmx):
        raise NotImplementedError

class RGBW12(DMXDevice):
    """
    Small RGBW fixture with 12 LEDs, 8 channels
    """

    def __init__(self, chan_no):
        super().__init__(chan_no, num_chans=8)
        self.r = 0
        self.g = 0
        self.b = 0
        self.w = 0

    def update(self, dmx):
        dmx[self.chan_no + 0] = 255     # Dimming
        dmx[self.chan_no + 1] = 0       # Strobe
        dmx[self.chan_no + 2] = 0       # DMX control
        dmx[self.chan_no + 3] = 0       # Speed
        dmx[self.chan_no + 4] = self.r
        dmx[self.chan_no + 5] = self.g
        dmx[self.chan_no + 6] = self.b
        dmx[self.chan_no + 7] = self.w

# TODO: should we have rgbw state, strobe in a base DMXFixture class?
# Most fixtures are going to support this?
# Except some are RGB, some RGBW?
# Refactoring can wait

dmx = DMXUniverse()
fix = RGBW12(chan_no=1)

fix.r = 255

fix.update(dmx)
