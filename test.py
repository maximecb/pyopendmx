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
            random.choice([255, 0]),
            random.choice([255, 0]),
            random.choice([255, 0]),
            random.choice([255, 0]),
        )

        if color != (0, 0, 0, 0):
            break

    return color






dmx = DMXUniverse()
fix = RGBW12(chan_no=1)

fix.r = 255
fix.g = 255
fix.b = 255
fix.w = 255











def dmx_thread_fn():
    # TODO: create DMX universe here?
    # We can keep a list of fixtures globally
    # Otherwise, create a start_dmx_thread method in the DMX universe
    # dmx.add_fixture()

    while True:
        print('dmx update', fix.r)
        fix.update(dmx)
        dmx.update()



dmx_thread = threading.Thread(target=dmx_thread_fn, args=(), daemon=True)
dmx_thread.start()





samplerate = 44100
win_s = 1024                # fft size
hop_s = win_s // 2          # hop size

a_tempo = aubio.tempo("default", win_s, hop_s, samplerate)
a_onset = aubio.onset("default", win_s, hop_s, samplerate)

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
        fix.r = r
        fix.g = g
        fix.b = b
        fix.w = w
    else:
        fix.r = int(fix.r * 0.8)
        fix.g = int(fix.g * 0.8)
        fix.b = int(fix.b * 0.8)
        fix.w = int(fix.w * 0.8)

    print('fix.r', fix.r)






stream.end()
