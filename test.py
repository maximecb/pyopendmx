import time
import math
#import pyftdi.serialext

from pyftdi.ftdi import Ftdi




port = Ftdi.create_from_url('ftdi://ftdi:232:AL6E8JFW/1')
port.reset()

port.set_baudrate(baudrate=250000)
port.set_line_property(bits=8, stopbit=2, parity='N', break_=False)

assert port.is_connected




# The 0th byte must be 0 (start code)
# 512 bytes are sent in total
data = bytearray(513 * [0])


data[1] = 255
data[5] = 255
data[6] = 0
data[7] = 255
data[8] = 0


itr = 0



while True:
    print('send')

    cyclepos = (itr % 50) / 50.0
    val = (math.sin(2 * math.pi * cyclepos) + 1) / 2

    # Strobe line
    data[1] = int(val * 255)

    port.set_break(True)
    port.set_break(False)
    port.write_data(data)



    time.sleep(20/1000.0)
    itr += 1




port.close()




