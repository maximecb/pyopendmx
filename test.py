import time
import math
from dmx import *

# IDEA: should we have rgbw state, strobe in a base DMXFixture class?
# Most fixtures are going to support this?
# Except some are RGB, some RGBW?
# Maybe wait to refactor until we play with the current setup a bit
# May want to use numpy to interpolate between configs

# TODO: function to map [0, 1] value into range, map_to()

dmx = DMXUniverse()
fix = RGBW12(chan_no=1)

fix.r = 255

fix.update(dmx)






"""
itr = 0

while True:
    print('send')

    cyclepos = (itr % 50) / 50.0
    val = (math.sin(2 * math.pi * cyclepos) + 1) / 2

    # Strobe line
    data[1] = int(val * 255)
"""
