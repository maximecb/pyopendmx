#!/usr/bin/env python3

import time
import math
import random
from dmx import *

#############################################################################

dmx = DMXUniverse()

spot = RGBWSpotLight(name="spot", chan_no=128)

dmx.add_device(spot)

dmx.start_dmx_thread()

while True:
    spot.rgbw = np.array([1, 1, 1, 1])
    time.sleep(1.0)

    spot.rgbw = np.array([0, 0, 0, 0])
    time.sleep(1.0)
