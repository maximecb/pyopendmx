#!/usr/bin/env python3

# Program is run on startup from 
# /home/pi/.bashrc

import time
import math
import random
from dmx import *
from utils import *

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

fix0 = dmx.add_device(RGBW12(name="fix0", chan_no=1))
fix1 = dmx.add_device(RGBW12(name="fix1", chan_no=10))
fix2 = dmx.add_device(RGBW12(name="fix2", chan_no=20))
fix3 = dmx.add_device(RGBW12(name="fix3", chan_no=30))
led_strip = dmx.add_device(LedStrip4CH(name="strip", chan_no=256))

dmx.start_dmx_thread()

fixs = [fix0, fix1, fix2, fix3]

#############################################################################

class SineAnim:
    def __init__(self):
        self.color0 = random_rgbw()
        self.color1 = random_rgbw()
        self.color2 = random_rgbw()
        self.color3 = random_rgbw()
        
        self.phase0 = (3 * math.pi) / 2
        self.phase1 = (3 * math.pi) / 2
        self.phase2 = (3 * math.pi) / 2
        self.phase3 = (3 * math.pi) / 2
        
        self.rate0 = random.uniform(0.20, 0.5)
        self.rate1 = random.uniform(0.20, 0.5)
        self.rate2 = random.uniform(0.20, 0.5)
        self.rate3 = random.uniform(0.20, 0.5)

    def update(self, t, dt):
        def update_phase(phase, rate, dt):
            return phase + (rate * 2 * math.pi * dt)

        self.phase0 = update_phase(self.phase0, self.rate0, dt)
        self.phase1 = update_phase(self.phase1, self.rate1, dt)
        self.phase2 = update_phase(self.phase2, self.rate2, dt)
        self.phase3 = update_phase(self.phase3, self.rate3, dt)
        
        fix0.rgbw = self.color0 * (1 + math.sin(self.phase0)) / 2
        fix1.rgbw = self.color1 * (1 + math.sin(self.phase1)) / 2
        fix2.rgbw = self.color2 * (1 + math.sin(self.phase2)) / 2
        fix3.rgbw = self.color3 * (1 + math.sin(self.phase3)) / 2

class StrobeAnim:
    def __init__(self):
        rgbw = random_rgbw()
        fix0.rgbw = rgbw
        fix1.rgbw = rgbw
        fix2.rgbw = rgbw
        fix3.rgbw = rgbw

        strobe_speed = random.uniform(0.65, 1.0)
        fix0.strobe = strobe_speed
        fix1.strobe = strobe_speed
        fix2.strobe = strobe_speed
        fix3.strobe = strobe_speed

        self.start_time = time.time()
        
    def update(self, t, dt):
        dt = t - self.start_time
        dimming = max(1 - (dt / 12), 0)
        fix0.dimming = dimming
        fix1.dimming = dimming
        fix2.dimming = dimming
        fix3.dimming = dimming

class SequenceAnim:
    def __init__(self):
        self.switch_delay = random.uniform(1, 4)
        self.switch_time = 0
        self.next_idx = 0
        
    def switch(self):
        self.switch_time = time.time()
        for fix in fixs:
            fix.dimming = 0
        fixs[self.next_idx].dimming = 1
        fixs[self.next_idx].rgbw = random_rgbw()
        self.next_idx = (self.next_idx + 1) % len(fixs)
        
    def update(self, t, dt):
        if t - self.switch_time > self.switch_delay:
            self.switch()

class PulseAnim:
    pass



animations = [
    SineAnim,
    StrobeAnim,
    SequenceAnim,
    #PulseAnim,
    #RedSine,
]

def change_anim():
    """
    Select a new random animation
    """

    global last_change
    global cur_anim

    print("changing animation")

    # Reset the state of each light
    for fix in fixs:
        fix.dimming = 1
        fix.strobe = 0
        fix.rgbw = np.array([0, 0, 0, 0])

    # Select a random animation class
    anim_class = random.choice(animations)

    last_change = time.time()
    cur_anim = anim_class()
    
    return cur_anim

lastT = time.time()
last_change = 0
change_delay = 10
cur_anim = None
change_anim()

while True:
    t = time.time()
    dt = t - lastT
    lastT = t
    #print(t)

    if is_night():
        print("night time")
        # TODO: set everything to black
        #continue

    if t - last_change > change_delay:
        change_anim()

    # Update the current animation
    cur_anim.update(t, dt)

    # Sleep 10ms
    time.sleep(0.01)

    # TODO:
    # Animate led_strip with slow sine, never quite goes to zero
    led_strip.ch0 = 1



    
