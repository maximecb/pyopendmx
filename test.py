import time
import math
import random
import threading
from dmx import *
from audio import *
import aubio






def random_color():
    pass



# IDEA: should we have rgbw state, strobe in a base DMXFixture class?
# Most fixtures are going to support this?
# Except some are RGB, some RGBW?
# Maybe wait to refactor until we play with the current setup a bit
# May want to use numpy to interpolate between configs

# TODO: function to map [0, 1] value into range, map_to()

dmx = DMXUniverse()
fix = RGBW12(chan_no=1)

fix.r = 255
fix.g = 255
fix.b = 255
fix.w = 255


# TODO: can we use librosa for FFT/mfccs in real-time?











def dmx_thread_fn():
    # TODO: create DMX universe here?

    while True:
        print('dmx update', fix.r)
        fix.update(dmx)
        dmx.update()



dmx_thread = threading.Thread(target=dmx_thread_fn, args=(), daemon=True)
dmx_thread.start()





samplerate = 11025
win_s = 512                 # fft size
hop_s = win_s // 2          # hop size

a_tempo = aubio.tempo("default", win_s, hop_s, samplerate)
a_onset = aubio.onset("default", win_s, hop_s, samplerate)

stream = sd.InputStream(samplerate=samplerate, blocksize=400, channels=1, dtype=np.float32, latency='low')
stream.start()

while True:
    beat_detected = False

    samples, overflowed = stream.read(hop_s)
    samples = samples.squeeze()


    # TODO: keep track of average intensity, stop when near silent
    #norm = np.linalg.norm(indata)*10

    # TODO: can we somehow smooth the tempo over time
    # Ideally, we would like a very regular beat
    # Could account for the average space between the last several beats somehow?

    # TODO: need a concept of beat events?
    # Send these events to an animation thread
    # Then, the DMX update thread does its thing separately



    beat = a_tempo(samples)

    if beat:
        print('|' * 40)
    else:
        print()

    if beat:
        val = 255
    else:
        val = int(fix.r * 0.7)

    #fix.strobe = val / 255
    fix.r = val
    fix.g = val
    fix.b = val
    fix.w = val

    print('fix.r', fix.r)






stream.end()
