#!/usr/bin/env python3

import time
import math
import random
import threading
import aubio
import numpy as np
import sounddevice as sd
from dmx import *

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

class Animation:
    """
    Store animation state and update the animation
    """

    def __init__(self, dmx):
        self.fix1 = RGBW12(name="fix1", chan_no=1)
        self.fix2 = RGBW12(name="fix2", chan_no=10)
        self.head1 = MovingHead(name="head1", chan_no=20)
        self.strip = LedStrip4CH(name="strip", chan_no=256)

        dmx.add_device(self.fix1)
        dmx.add_device(self.fix2)
        dmx.add_device(self.head1)
        dmx.add_device(self.strip)

        self.head1.dimming = 0.20
        self.head1.speed = 0.25

        self.head1.pan = 0.33
        self.head1.tilt = 0

    def update(self, beat, beat_no, loudness, loud_vals):
        """
        Update the animation
        """

        max_loudness = max(loud_vals)

        fix1 = self.fix1
        fix2 = self.fix2
        head = self.head1
        strip = self.strip

        #fix1.strobe = 1
        #fix2.strobe = 1
        #head.strobe = 0.95

        if beat:
            rgbw = random_rgbw()

            fix1_on, fix2_on = random.choice([
                [1, 0],
                [0, 1],
                [1, 1]
            ])

            if fix1_on:
                fix1.rgbw = rgbw
            if fix2_on:
                fix2.rgbw = rgbw
            
            head.rgbw = rgbw
            #if beat_no % 4 == 0:

            #head.pan = np.clip(head.pan + random.uniform(-0.1, 0.1), 0.15, 0.50)
            #head.tilt = np.clip(head.tilt + random.uniform(-0.1, 0.1), 0.00, 0.40)

            if beat_no % 2 == 0:
                head.pan = random.uniform(0.15, 0.50)
                head.tilt = random.uniform(0.00, 0.40)



        else:
            # Decay
            fix1.rgbw = fix1.rgbw * 0.7
            fix2.rgbw = fix2.rgbw * 0.7
            head.rgbw = head.rgbw * 0.95
            pass

#############################################################################

dmx = DMXUniverse()

anim = Animation(dmx)

dmx.start_dmx_thread()

samplerate = 44100
win_s = 1024                # fft size
hop_s = win_s // 2          # hop size

a_tempo = aubio.tempo("default", win_s, hop_s, samplerate)

stream = sd.InputStream(samplerate=samplerate, blocksize=400, channels=1, dtype=np.float32, latency='low')
stream.start()

beat_no = 0
loud_vals = []

while True:
    beat_detected = False

    samples, overflowed = stream.read(hop_s)
    samples = samples.squeeze()

    loudness = np.std(samples)
    loud_vals.append(loudness)

    if (len(loud_vals) > 500):
        loud_vals.pop(0)

    print(loudness)

    # Loudness threshold for beat detection
    # Stops beats when the music stops
    if max(loud_vals[-10:]) < 0.05:
        beat = False
    else:
        # Note: we can call o.get_last_s() to get the sample where the beat occurred
        beat = a_tempo(samples)

    anim.update(beat, beat_no, loudness, loud_vals)

    if beat:
        print('|' * 40)
        beat_no += 1
    else:
        print()

stream.end()
