#!/usr/bin/env python3

import time
import math
import random
import threading
import aubio
import numpy as np
from collections import namedtuple
import sounddevice as sd
from dmx import *

Sine = namedtuple("sine", ("rate", "phase", "mid", "ampl"))

class Animation:
    """
    Store animation state and update the animation
    """

    def __init__(self, dmx):
        self.fix1 = RGB36(name="fix1", chan_no=100)
        self.fix2 = RGB36(name="fix2", chan_no=110)
        self.fix3 = RGB36(name="fix3", chan_no=120)
        self.fix4 = RGB36(name="fix4", chan_no=130)
        self.fixs = [self.fix1, self.fix2, self.fix3, self.fix4]

        self.head1 = MiniGobo9CH(name="head1", chan_no=32)
        self.head2 = MiniGobo9CH(name="head2", chan_no=64)
        self.heads = [self.head1, self.head2]

        # Blacklight fixture
        self.uv = RGBW54(name="uv", chan_no=10)

        self.strip = LedStrip4CH(name="strip", chan_no=256)

        for fix in self.fixs:
            dmx.add_device(fix)
        for head in self.heads:
            dmx.add_device(head)
        dmx.add_device(self.uv)
        dmx.add_device(self.strip)

        self.dmx = dmx

        self.next_update = [0] * len(dmx.devices)

        self.sines = []
        for i in range(len(dmx.devices)):
            sine = Sine(
                rate = random.uniform(0.05, 0.15),
                phase = random.uniform(0, math.pi),
                mid = 0.5,
                ampl = 0.48
            )
            self.sines.append(sine)

        # Set initial color to red
        for fix in self.fixs:
            fix.rgb = np.array([1, 0, 0])
        self.uv.rgbw = np.array([1, 1, 1, 1])
        self.strip.ch1 = 0.8

    def update(self):
        """
        Update the animation
        """

        t = time.time()
        #print(t)

        for (idx, dev) in enumerate(self.dmx.devices):
            if t < self.next_update[idx]:
                continue

            if isinstance(dev, MiniGobo9CH):
                dev.dimming = 1
                dev.speed = 1 / 255
                dev.color = 1 # red color, 0 for white
                dev.gobo = 2 # plain circle
                dev.pan = random.uniform(0.5, 0.9)
                dev.tilt = random.uniform(0.7, 1.0)

            self.next_update[idx] = t + random.uniform(3, 6)

        for (idx, dev) in enumerate(self.dmx.devices):
            # Compute the sine value
            s = self.sines[idx]
            val = s.mid + math.sin(s.phase + s.rate * 2 * math.pi * t) * s.ampl

            print(val)

            dev.dimming = val








#############################################################################

dmx = DMXUniverse()

anim = Animation(dmx)

dmx.start_dmx_thread()

while True:
    anim.update()
    time.sleep(1.0 / 30.0)
