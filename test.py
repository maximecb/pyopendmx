import time
import math
from dmx import *
from audio import *

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



def process_sound(indata, frames, time, status):
    print(indata.shape)

    norm = np.linalg.norm(indata)*10
    norm = min(norm, 100)

    print(norm)
    print("|" * int(norm))


    if norm > 40:
        val = 255
    else:
        val = 0

    fix.r = val
    fix.g = val
    fix.b = val
    fix.w = val

    fix.update(dmx)
    dmx.update()
    


stream = sd.InputStream(samplerate=11025, blocksize=400, channels=1, dtype=np.float32, latency='low')
stream.start()

while True:

    num_avail = stream.read_available
    print(num_avail)
    data, overflowed = stream.read(max(num_avail, 400))
    num_read = data.shape[0]

    start_idx = num_read - 400
    print(start_idx)

    data = data[start_idx:, :]

    print(data.shape)

    process_sound(data, 0, 0, 0)


stream.end()

