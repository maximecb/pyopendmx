# pyopendmx

Music-reactive DMX experiment with an [ENTTEC OpenDMX](https://www.enttec.com/product/controls/dmx-usb-interfaces/open-dmx-usb/) (USB to DMX interface) using the pyftdi and aubio libraries. This code is designed to run on a Raspberry Pi 4 but will also run on more powerful x86 machines. I personally use an affordable (~$35) clone of the ENTTEC OpenDMX which I found on eBay, simply search
your favorite merchant website for "OpenDMX" to find options.

# Installation

```
# On MacOS, install required libraries
brew install --build-from-source libusb

# On Ubuntu or Raspbian, install required libraries
sudo apt-get install libportaudio2

# Install required Python packages
pip3 install pyftdi numpy sounddevice aubio
```

# Usage

The `dmx.py` source file contains reusable code to interface with DMX devices using an OpenDMX FTDI interface.

The `anim_beatdetect.py` script contains my own code to animate lights based on beat detection, which you can take inspiration from.
