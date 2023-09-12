#!/usr/bin/env python3

import time
import math
import random
import threading
import aubio
import numpy as np
import sounddevice as sd
from dmx import *

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

        for fix in self.fixs:
            dmx.add_device(fix)
        for head in self.heads:
            dmx.add_device(head)

    def gen_sequence(self, num_steps, num_elems):
        """
        Ideally what we want is a vector
        [num_steps, num_elems, 4]
        We could start by just genetating colors and then masking
        """

        seq = np.zeros(shape=(num_steps, num_elems, 4))

        for step in range(0, num_steps):
            # Pick one color for this step
            color = random_rgbw()

            # Generate a mask with at least one nonzero element
            while True:
                mask = np.random.choice(a=[0, 1], size=(num_elems,), p=[0.5, 0.5])
                if mask.any():
                    break

            for elem in range(0, num_elems):
                seq[step, elem] = color * mask[elem]

        return seq

    def update(self, beat, beat_no, loudness, loud_vals):
        """
        Update the animation
        """

        max_loudness = max(loud_vals)

        #head = self.head1

        #fix1.strobe = 1
        #fix2.strobe = 1
        #head.strobe = 0.95

        if beat:
            """
            # Every 4 bars
            if beat_no % 16 == 0:
                self.fix_seq = self.gen_sequence(num_steps=4, num_elems=2)

            # Every 2 beats
            if beat_no % 2 == 0:
                head.pan = random.uniform(0.15, 0.50)
                head.tilt = random.uniform(0.00, 0.40)
            """

            rgb = random_rgb()

            #fix1.rgbw = self.fix_seq[beat_no % 4, 0]
            #fix2.rgbw = self.fix_seq[beat_no % 4, 1]
            #head.rgbw = rgbw

            fixs = random.choices(self.fixs, k = random.randint(1, 4))
            for fix in fixs:
                fix.rgb = rgb

            for head in self.heads:
                head.dimming = 1
                head.speed = 0.01
                if beat_no % 4 == 0:
                    head.color = random.randint(0, 7)
                    head.gobo = random.randint(0, 7)

                if beat_no % 4 == 0:
                    head.pan = random.uniform(0.5, 0.9)
                    head.tilt = random.uniform(0.7, 1.0)



        else:
            # Decay
            for fix in self.fixs:
                fix.rgb = fix.rgb * 0.86



            #fix2.rgbw = fix2.rgbw * 0.7
            #head.rgbw = head.rgbw * 0.95
            #strip.ch1 = strip.ch1 * 0.8
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
