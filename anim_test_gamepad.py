#!/usr/bin/env python3

import time
import math
import random
from dmx import *
from gamepad import *

#############################################################################

dmx = DMXUniverse()

fix1 = RGB36(name="fix1", chan_no=100)
fix2 = RGB36(name="fix2", chan_no=110)
fix3 = RGB36(name="fix3", chan_no=120)
fix4 = RGB36(name="fix4", chan_no=130)
fixs = [fix1, fix2, fix3, fix4]

for fix in fixs:
    dmx.add_device(fix)

pad = GamePad()

dmx.start_dmx_thread()

# TODO: need to close poll fds

"""
while True:
    while pad.event_avail():
        type, number, value = pad.read_event()
        print(type, number, value)

        if type == 'button' and value == 1:
            for fix in fixs:
                fix.rgb = random_rgb()

    time.sleep(0.25)

    for fix in fixs:
        fix.rgb = np.array([0, 0, 0])
"""


while True:
    type, number, value = pad.read_event()
    print(type, number, value)

    if type == 'button' and value == 1:
        if number == 0:
            color = np.array([0, 1, 0])
        elif number == 1:
            color = np.array([1, 0, 0])
        elif number == 2:
            color = np.array([0, 0, 1])
        else:
            color = np.array([1, 1, 0])

        for fix in fixs:
            fix.rgb = color

    if type == 'button' and value == 0:
        for fix in fixs:
            fix.rgb = np.array([0, 0, 0])
