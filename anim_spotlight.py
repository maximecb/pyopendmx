#!/usr/bin/env python3

import time
import math
import random
from dmx import *

#############################################################################

dmx = DMXUniverse()

uv = RGBW54(name="uv", chan_no=10)

dmx.add_device(uv)

dmx.start_dmx_thread()

while True:
    uv.rgbw = np.array([1, 1, 1, 1])
    time.sleep(1.0)

    uv.rgbw = np.array([0, 0, 0, 0])
    time.sleep(1.0)
