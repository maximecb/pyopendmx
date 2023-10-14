import time
import random
import threading
from pyftdi.ftdi import Ftdi
import numpy as np

def random_rgb():
    while True:
        color = np.array([
            random.choice([1, 0]),
            random.choice([1, 0]),
            random.choice([1, 0]),
        ])

        if color.any():
            break

    return color

def random_rgbw():
    while True:
        color = np.array([
            random.choice([1, 0]),
            random.choice([1, 0]),
            random.choice([1, 0]),
            random.choice([1, 0]),
        ])

        if color.any():
            break

    return color

def map_to(val, min, max):
    assert max > min
    val = np.clip(val, 0, 1)
    return int(round(min + val * (max - min)))

def show_devices():
    """
    List available FTDI devices
    """

    Ftdi.show_devices()

class DMXUniverse:
    """
    Interface to an ENTTEC OpenDMX (FTDI) DMX interface
    """
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

    def set_int(self, start_chan, chan_no, int_val):
        self[start_chan + chan_no - 1] = int_val

    def set_float(self, start_chan, chan_no, val, min=0, max=255):
        assert (chan_no >= 1)

        # If val is an array of values
        if hasattr(val, '__len__'):
            for i in range(len(val)):
                int_val = map_to(val[i], min, max)
                self[start_chan + chan_no - 1 + i] = int_val
        else:
            int_val = map_to(val, min, max)
            self[start_chan + chan_no - 1] = int_val

    def add_device(self, device):
        # Check for partial channel overlaps between devices, which
        # are probably an error
        for other in self.devices:
            # Two devices with the same type and the same channel are probably ok
            if device.chan_no == other.chan_no and type(device) == type(other):
                continue

            if device.chan_overlap(other):
                raise Exception('partial channel overlap between devices "{}" and "{}"'.format(device.name, other.name))

        self.devices.append(device)
        return device

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
        assert (chan_no >= 1)
        self.name = name
        self.chan_no = chan_no
        self.num_chans = num_chans

    def chan_overlap(this, that):
        """
        Check if two devices have overlapping channels
        """

        this_last = this.chan_no + (this.num_chans - 1)
        that_last = that.chan_no + (that.num_chans - 1)

        return (
            (this.chan_no >= that.chan_no and this.chan_no <= that_last) or
            (that.chan_no >= this.chan_no and that.chan_no <= this_last)
        )

    def update(self, dmx):
        raise NotImplementedError

class RGBWSpotLight(DMXDevice):
    """
    Small RGBW spotlight
    NOTE: needs to be set in mode A_xxx for DMX control
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
        self.rgbw = np.array([0, 0, 0, 0])
        self.strobe = 0

    def update(self, dmx):
        if self.strobe == 0:
            dmx.set_float(self.chan_no, 1, 134)
        else:
            dmx.set_float(self.chan_no, 1, self.strobe, 135, 191)

        dmx.set_float(self.chan_no, 2, self.rgbw * self.dimming)

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
        self.rgbw = np.array([0, 0, 0, 0])
        self.strobe = 0

    def update(self, dmx):
        dmx.set_float(self.chan_no, 1, self.dimming)
        dmx.set_float(self.chan_no, 2, self.strobe, 0, 191)
        dmx.set_float(self.chan_no, 3, 0)
        dmx.set_float(self.chan_no, 4, 0)
        dmx.set_float(self.chan_no, 5, self.rgbw)

class RGB36(DMXDevice):
    """
    RGB fixture with 36 LEDs, 6 channels
    CH1: total dimming
    CH2: R 0-255
    CH3: G 0-255
    CH4: B 0-255
    CH5: strobe speed (0-255)
    CH6: color change speed (0-255)
    """

    def __init__(self, name, chan_no):
        super().__init__(name, chan_no, num_chans=8)
        self.dimming = 1
        self.rgb = np.array([0, 0, 0])
        self.strobe = 0
        self.anim_speed = 0

    def update(self, dmx):
        dmx.set_float(self.chan_no, 1, self.dimming)
        dmx.set_float(self.chan_no, 2, self.rgb)
        dmx.set_float(self.chan_no, 5, self.strobe, 0, 255)
        dmx.set_float(self.chan_no, 6, self.anim_speed, 0, 255)

class RGBW54(DMXDevice):
    """
    RGBW fixture with 54 LEDs, in 4 channel mode
    CH1: R 0-255
    CH2: G 0-255
    CH3: B 0-255
    CH4: W 0-255
    """

    def __init__(self, name, chan_no):
        super().__init__(name, chan_no, num_chans=4)
        self.dimming = 1
        self.rgbw = np.array([0, 0, 0, 0])

    def update(self, dmx):
        rgbw = self.rgbw * self.dimming
        dmx.set_float(self.chan_no, 1, rgbw)

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

    Pan:
    0.00 is pointing back
    0.15 is pointing left
    0.33 is pointing forward
    0.50 is pointing right

    Tilt:
    0.00 is pointing forward
    0.50 is fully up
    1.00 is pointing back
    """

    def __init__(self, name, chan_no):
        super().__init__(name, chan_no, num_chans=14)
        self.pan = 0
        self.tilt = 0
        self.speed = 0
        self.dimming = 1
        self.rgbw = np.array([0, 0, 0, 0])
        self.strobe = 0

    def update(self, dmx):
        dmx.set_float(self.chan_no, 1, self.pan)
        dmx.set_float(self.chan_no, 2, self.tilt)
        dmx.set_float(self.chan_no, 3, 1 - self.speed)
        dmx.set_float(self.chan_no, 4, self.dimming)
        dmx.set_float(self.chan_no, 5, self.strobe)
        dmx.set_float(self.chan_no, 6, self.rgbw)

class MiniGobo9CH(DMXDevice):
    """
    Mini gobo moving head with color wheel.

    CH1: motor pan
    CH2: motor tilt
    CH3: color wheel control, 0-127 for fixed color selection
    CH4: gobo wheel control, 0-63 for fixed gobo selection

    CH5: light control, 0 is off, 15 is on.
    CH6: dimming
    CH7: pan/tilt speed 0-255 (fast to slow)
    CH8: function control
    CH9: effects

    Pan:
    0.00 is pointing back
    0.15 is pointing left
    0.33 is pointing forward
    0.50 is pointing right

    Tilt:
    0.00 is pointing forward
    0.50 is fully up
    1.00 is pointing back
    """

    def __init__(self, name, chan_no):
        super().__init__(name, chan_no, num_chans=9)
        self.pan = 0
        self.tilt = 0
        self.speed = 0.5
        self.dimming = 0
        self.gobo = 0
        self.color =  0

    def update(self, dmx):
        dmx.set_float(self.chan_no, 1, self.pan)
        dmx.set_float(self.chan_no, 2, self.tilt)

        # Color wheel
        # There are 8 colors, with indices in [0, 7]
        dmx[self.chan_no + 3 - 1] = self.color * 16

        # Gobo wheel
        # There are 8 gobos, with indices in [0, 7]
        dmx[self.chan_no + 4 - 1] = self.gobo * 8

        # Color control (on/off)
        dmx[self.chan_no + 5 - 1] = 15

        # Dimming/brightness
        dmx.set_float(self.chan_no, 6, self.dimming)

        # Rotation speed
        dmx.set_float(self.chan_no, 7, 1 - self.speed)

        # Function control
        dmx.set_float(self.chan_no, 8, 0)

class LedStrip4CH(DMXDevice):
    """
    4-channel DMX LED strip decoder
    CH1: R 0-255
    CH2: G 0-255
    CH3: B 0-255
    CH4: W 0-255
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

class Relay3CH(DMXDevice):
    """
    3-channel on/off relay decoder
    CH1: 0 or 1
    CH2: 0 or 1
    CH3: 0 or 1
    """

    def __init__(self, name, chan_no):
        super().__init__(name, chan_no, num_chans=4)
        self.ch1 = 0
        self.ch2 = 0
        self.ch3 = 0

    def update(self, dmx):
        dmx[self.chan_no + 0] = 255 if self.ch1 else 0
        dmx[self.chan_no + 1] = 255 if self.ch2 else 0
        dmx[self.chan_no + 2] = 255 if self.ch3 else 0

class R1200L(DMXDevice):
    """
    Rockville R1200L smoke machine
    CH1: fog burst control
    CH2: red
    CH3: green
    CH4: blue
    CH5: strobe speed
    CH6: dimming
    CH7: sound response
    """

    def __init__(self, name, chan_no):
        super().__init__(name, chan_no, num_chans=7)
        self.fog = 0
        self.dimming = 1
        self.rgb = np.array([0, 0, 0])
        self.strobe = 0

    def update(self, dmx):
        dmx.set_float(self.chan_no, 1, self.fog)
        dmx.set_float(self.chan_no, 2, self.rgb * self.dimming)
        dmx.set_float(self.chan_no, 5, self.strobe)
        # Dimming/function/sound control
        # The manual seems inaccurate, this has to be set to 0
        dmx.set_int(self.chan_no, 6, 0)
        # Sound response
        dmx.set_int(self.chan_no, 7, 0)
