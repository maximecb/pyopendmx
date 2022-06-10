#!/usr/bin/env python3

# Program is run on startup from 
# /home/pi/.bashrc

import time
import math
import random
from dmx import *

#############################################################################

def random_rgbw():
    while True:
        color = np.array([
            random.choice([1, 0]),
            random.choice([1, 0]),
            random.choice([1, 0]),
            random.choice([1, 0]),
        ])

        if color.any():
            break

    return color

#############################################################################

dmx = DMXUniverse()

#relay3ch = Relay3CH(name="strip", chan_no=128)
#dmx.add_device(relay3ch)

fix0 = RGBW12(name="fix0", chan_no=1)
dmx.add_device(fix0)

dmx.start_dmx_thread()




while True:
    pass
    
    rgbw = random_rgbw()

    fix0.rgbw = rgbw
    time.sleep(0.5)
    
    fix0.rgbw = np.array([0, 0, 0, 0])
    time.sleep(0.5)
