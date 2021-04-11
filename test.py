import time
import math
import random
import threading
from dmx import *
from audio import *
import aubio






def random_color():
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






dmx = DMXUniverse()

fix = RGBW12(chan_no=1)
head = MovingHead(chan_no=1)

dmx.add_device(fix)
#dmx.add_device(head)

dmx.start_dmx_thread()






samplerate = 44100
win_s = 1024                # fft size
hop_s = win_s // 2          # hop size

a_tempo = aubio.tempo("default", win_s, hop_s, samplerate)

stream = sd.InputStream(samplerate=samplerate, blocksize=400, channels=1, dtype=np.float32, latency='low')
stream.start()

while True:
    beat_detected = False

    samples, overflowed = stream.read(hop_s)
    samples = samples.squeeze()

    beat = a_tempo(samples)
    # Can call o.get_last_s() to get the sample where the beat occurred

    if beat:
        print('|' * 40)
    else:
        print()

    if beat:
        r, g, b, w = random_color()

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

        # TODO: only change position ever 2 or 4 beats
        head.speed = 0.25
        head.dimming = 0.25
        head.pan = random.uniform(0, 1)
        head.tilt = random.uniform(0.4, 0.6)

    else:
        head.dimming = head.dimming * 0.7
        fix.dimming = fix.dimming * 0.8



stream.end()
