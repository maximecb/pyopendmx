# pyopendmx

Music-reactive DMX experiment with an [ENTTEC OpenDMX](https://www.enttec.com/product/controls/dmx-usb-interfaces/open-dmx-usb/) (USB to DMX interface) using the pyftdi and aubio libraries. This code is designed to run on a Raspberry Pi but will also run on more powerful x86 machines.

```
sudo apt-get install libportaudio2

pip3 install pyftdi numpy sounddevice aubio
```

See `dmx.py` for code to interface with DMX devices using an OpenDMX ftdi interface.
