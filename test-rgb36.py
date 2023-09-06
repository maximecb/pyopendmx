#!/usr/bin/env python3

import time
import math
import random
from dmx import *

#############################################################################

dmx = DMXUniverse()

fix1 = RGB36(name="fix1", chan_no=100)
fix2 = RGB36(name="fix2", chan_no=110)
fix3 = RGB36(name="fix3", chan_no=120)
fix4 = RGB36(name="fix4", chan_no=130)
fixs = [fix1, fix2, fix3, fix4]

for fix in fixs:
    dmx.add_device(fix)

dmx.start_dmx_thread()

while True:
    for fix in fixs:
        fix.rgb = random_rgb()
        time.sleep(1.0)

        fix.rgb = np.array([0, 0, 0])
        time.sleep(1.0)
