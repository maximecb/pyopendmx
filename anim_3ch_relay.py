#!/usr/bin/env python3

import time
import math
import random
from dmx import *

#############################################################################

dmx = DMXUniverse()

relay3ch = Relay3CH(name="strip", chan_no=128)

dmx.add_device(relay3ch)

dmx.start_dmx_thread()


while True:
    relay3ch.ch1 = 1
    time.sleep(0.5)
    relay3ch.ch1 = 0
    time.sleep(0.5)

    relay3ch.ch2 = 1
    time.sleep(0.5)
    relay3ch.ch2 = 0
    time.sleep(0.5)
