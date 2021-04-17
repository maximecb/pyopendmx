import time
import math
import threading
from pyftdi.ftdi import Ftdi
import numpy as np

def map_to(val, min, max):
    assert max > min
    val = np.clip(val, 0, 1)
    return int(round(min + val * (max - min)))

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

        self.devices = []

    def __del__(self):
        self.port.close()

    def __setitem__(self, idx, val):
        assert (idx >= 1)
        assert (idx <= 512)
        assert isinstance(val, int)
        assert (val >= 0 and val <= 255)
        self.data[idx] = val

    def set_float(self, start_chan, chan_no, val, min=0, max=255):
        assert (chan_no >= 1)

        if hasattr(val, '__len__'):
            for i in range(len(val)):
                int_val = map_to(val[i], min, max)
                self[start_chan + chan_no - 1 + i] = int_val
        else:
            int_val = map_to(val, min, max)
            self[start_chan + chan_no - 1] = int_val

    def add_device(self, device):
        self.devices.append(device)

    def start_dmx_thread(self):
        """
        Thread to write channel data to the output port
        """

        def dmx_thread_fn():
            while True:
                for dev in self.devices:
                    dev.update(self)

                self.port.set_break(True)
                self.port.set_break(False)
                self.port.write_data(self.data)

                # The maximum update rate for the Enttec OpenDMX is 40Hz
                time.sleep(8/1000.0)

        dmx_thread = threading.Thread(target=dmx_thread_fn, args=(), daemon=True)
        dmx_thread.start()

class DMXDevice:
    def __init__(self, name, chan_no, num_chans):
        self.name = name
        self.chan_no = chan_no
        self.num_chans = num_chans

    def update(self, dmx):
        raise NotImplementedError

class RGBWSpotLigh(DMXDevice):
    """
    Small RGBW spotlight
    CH1: effect (0 no effect, 135-239 strobe)
    CH2: R 0-255
    CH3: G 0-255
    CH4: B 0-255
    CH5: W 0-255
    CH6: modes
    """

    def __init__(self, name, chan_no):
        super().__init__(name, chan_no, num_chans=6)
        self.dimming = 1
        self.r = 0
        self.g = 0
        self.b = 0
        self.w = 0
        self.strobe = 0

    def update(self, dmx):
        if self.strobe == 0:
            dmx.set_float(self.chan_no, 1, 0)
        else:
            dmx.set_float(self.chan_no, 1, strobe, 135, 191)

        dmx.set_float(self.chan_no, 2, self.r * self.dimming)
        dmx.set_float(self.chan_no, 3, self.g * self.dimming)
        dmx.set_float(self.chan_no, 4, self.b * self.dimming)
        dmx.set_float(self.chan_no, 5, self.w * self.dimming)

class RGBW12(DMXDevice):
    """
    Small RGBW fixture with 12 LEDs, 8 channels
    CH1: total dimming
    CH2: strobe (0-2 off, 3-191 slow to fast)
    CH3: function select (0-50 DMX)
    CH4: function speed
    CH5: R 0-255
    CH6: G 0-255
    CH7: B 0-255
    CH8: W 0-255
    """

    def __init__(self, name, chan_no):
        super().__init__(name, chan_no, num_chans=8)
        self.dimming = 1
        self.r = 0
        self.g = 0
        self.b = 0
        self.w = 0
        self.strobe = 0

    def update(self, dmx):
        dmx.set_float(self.chan_no, 1, self.dimming)
        dmx.set_float(self.chan_no, 2, self.strobe, 0, 191)
        dmx.set_float(self.chan_no, 3, 0)
        dmx.set_float(self.chan_no, 4, 0)
        dmx.set_float(self.chan_no, 5, self.r)
        dmx.set_float(self.chan_no, 6, self.g)
        dmx.set_float(self.chan_no, 7, self.b)
        dmx.set_float(self.chan_no, 8, self.w)

class MovingHead(DMXDevice):
    """
    Moving head with RGBW and strobe.
    Modeled after the Docooler mini moving head
    CH1: motor pan
    CH2: motor tilt
    CH3: pan/tilt speed 0-255 (fast to slow)
    CH4: total dimming
    CH5: strobe speed
    CH6: R 0-255
    CH7: G 0-255
    CH8: B 0-255
    CH9: W 0-255
    """

    def __init__(self, name, chan_no):
        super().__init__(name, chan_no, num_chans=14)
        self.pan = 0
        self.tilt = 0
        self.speed = 0
        self.dimming = 1
        self.r = 0
        self.g = 0
        self.b = 0
        self.w = 0
        self.strobe = 0

    def update(self, dmx):
        dmx.set_float(self.chan_no, 1, self.pan)
        dmx.set_float(self.chan_no, 2, self.tilt)
        dmx.set_float(self.chan_no, 3, 1 - self.speed)
        dmx.set_float(self.chan_no, 4, self.dimming)
        dmx.set_float(self.chan_no, 5, self.strobe)
        dmx.set_float(self.chan_no, 6, self.r)
        dmx.set_float(self.chan_no, 7, self.g)
        dmx.set_float(self.chan_no, 8, self.b)
        dmx.set_float(self.chan_no, 9, self.w)

class LedStrip4CH(DMXDevice):
    """
    4-channel DMX LED strip decoder
    CH1: CH1/R 0-255
    CH2: CH2/G 0-255
    CH3: CH3/B 0-255
    CH4: CH4/W 0-255
    """

    def __init__(self, name, chan_no):
        super().__init__(name, chan_no, num_chans=4)
        self.dimming = 1
        self.ch1 = 0
        self.ch2 = 0
        self.ch3 = 0
        self.ch4 = 0

    def update(self, dmx):
        dmx.set_float(self.chan_no, 1, self.ch1 * self.dimming)
        dmx.set_float(self.chan_no, 2, self.ch2 * self.dimming)
        dmx.set_float(self.chan_no, 3, self.ch3 * self.dimming)
        dmx.set_float(self.chan_no, 4, self.ch4 * self.dimming)
