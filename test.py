import time
import math
#import pyftdi.serialext

from pyftdi.ftdi import Ftdi




port = Ftdi.create_from_url('ftdi://ftdi:232:AL6E8JFW/1')


#open_bitbang_from_url(url, direction=0, latency=16, baudrate=1000000, sync=False)
#open_bitbang(vendor, product, bus=None, address=None, index=0, serial=None, interface=1, direction=0, latency=16, baudrate=1000000, sync=False)


port.set_baudrate(baudrate=250000)
port.set_line_property(bits=8, stopbit=2, parity='N', break_=False)



assert port.is_connected




# The 0th byte must be 0 (start code)
# 512 bytes are sent in total
data = bytearray(513 * [0])


data[1] = 255
data[5] = 255
data[6] = 255
data[7] = 255
data[8] = 255


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






# Send bytes
#port.write(b'Hello World')












#import pyftdi.ftdi
#ftdi = pyftdi.ftdi.Ftdi()
#print(ftdi.show_devices())
#ftdi://ftdi:232:AL6E8JFW/1

#ftDCB.BaudRate = 250000;
#status = FT_SetDataCharacteristics(handle, BITS_8, STOP_BITS_2, PARITY_NONE);
#status = FT_SetFlowControl(handle, (char)FLOW_NONE, 0, 0);
#status = FT_ClrRts(handle);
#status = FT_Purge(handle, PURGE_TX);
#status = FT_Purge(handle, PURGE_RX);




#'ftdi://ftdi:232/1',
#'ftdi://ftdi:232:AL6E8JFW/1',
#baudrate=250000,
#bytesize=8,
#stopbits=2,
#parity='N',
#xonxoff=0,
#rtscts=0


