import time
import math
import random
import threading
from dmx import *
from audio import *
import aubio

def random_rgb():
    while True:
        color = (
            random.choice([1, 0]),
            random.choice([1, 0]),
            random.choice([1, 0]),
        )

        if color != (0, 0, 0):
            break

    return color

def random_rgbw():
    while True:
        color = (
            random.choice([1, 0]),
            random.choice([1, 0]),
            random.choice([1, 0]),
            random.choice([1, 0]),
        )

        if color != (0, 0, 0, 0):
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
            r, g, b, w = random_rgbw()

            fix.dimming = 1
            fix.r = r
            fix.g = g
            fix.b = b
            fix.w = w

            head.dimming = 1
            head.r = r
            head.g = g
            head.b = b
            head.w = w

            # TODO: only change position every 2 or 4 beats
            head.speed = 0.25
            head.dimming = 0.25
            head.pan = random.uniform(0, 1)
            head.tilt = random.uniform(0.4, 0.6)

            strip.dimming = 1
            strip.ch1 = 1

        else:
            # Decay
            head.dimming = head.dimming * 0.7
            fix.dimming = fix.dimming * 0.8
            strip.dimming = strip.dimming * 0.7

        #new_dimming = (loudness / max_loudness) ** 4
        #strip.dimming = new_dimming
        #strip.ch1 = 1






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
