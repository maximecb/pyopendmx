import struct
import select

# This uses the old Linux joystick API, e.g. /dev/input.js0
# https://www.kernel.org/doc/Documentation/input/joystick-api.txt
#
# struct js_event {
#     __u32 time;     /* event timestamp in milliseconds */
#     __s16 value;    /* value */
#     __u8 type;      /* event type */
#     __u8 number;    /* axis/button number */
# };

class GamePad:
    def __init__(self, dev_path="/dev/input/js0"):
        self.dev = open(dev_path, "rb")
        self.poll = select.poll()
        self.poll.register(self.dev, select.POLLIN)

    def event_avail(self):
        """
        Check if events are available without blocking
        """

        events = self.poll.poll(0)
        return len(events) > 0

    def read_event(self):
        """
        Read a single event (blocking)
        """

        bytes = self.dev.read(8)

        # 4 bytes, 2 bytes, 1 byte, 1 byte
        t, value, type, number = struct.unpack("<IhBB", bytes)

        # t: time in ms
        # index: button/axis number (0 for x-axis)
        # code: 1 for buttons, 2 for axis
        # value: axis position, 0 for center, 1 for buttonpress, 0 for button release
        #print("t: {:10d} ms, type: {:03d}, number: {:03d}, value: {:6d}, ".format(t, type, number, value))

        if type == 1:
            type = 'button'
        elif type == 2:
            type = 'axis'
        else:
            type = 'init'

        return type, number, value
