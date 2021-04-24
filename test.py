#!/usr/bin/env python3

import time
import math
import random
import threading
from dmx import *
from audio import *
import aubio

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
        self.fix = RGBW12(name="fix", chan_no=1)
        self.strip = LedStrip4CH(name="strip", chan_no=256)
        self.head = MovingHead(name="head", chan_no=1)

        dmx.add_device(self.fix)
        dmx.add_device(self.strip)
        #dmx.add_device(self.head)

    def update(self, beat, beat_no, loudness, loud_vals):
        """
        Update the animation
        """

        max_loudness = max(loud_vals)

        fix = self.fix
        strip = self.strip
        head = self.head

        if beat:
            rgbw = random_rgbw()

            fix.rgbw = rgbw

            # TODO: only change position every 2 or 4 beats
            # Maybe go on and off every 2 beats or some such?
            #head.rgbw = rgbw
            #head.speed = 0.25
            #head.dimming = 0.25
            #head.pan = random.uniform(0, 1)
            #head.tilt = random.uniform(0.4, 0.6)

            strip.ch1 = 1

        else:
            # Decay
            fix.rgbw = fix.rgbw * 0.7
            strip.ch1 = strip.ch1 * 0.7

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

    # Loudness threshold for beat detection
    # Stops beats when the music stops
    if max(loud_vals[-10:]) < 0.1:
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
