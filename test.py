import pyftdi.serialext

# S/N: AL6E8JFW

# Open a serial port on the second FTDI device interface (IF/1)
port = pyftdi.serialext.serial_for_url('ftdi://ftdi:2232h/1', baudrate=250000)






#ftDCB.BaudRate = 250000;
#status = FT_SetDataCharacteristics(handle, BITS_8, STOP_BITS_2, PARITY_NONE);
#status = FT_SetFlowControl(handle, (char)FLOW_NONE, 0, 0);
#status = FT_ClrRts(handle);
#status = FT_Purge(handle, PURGE_TX);
#status = FT_Purge(handle, PURGE_RX);





# The 0th byte must be 0 (start code)
# 512 bytes are sent in total

# Send bytes
#port.write(b'Hello World')


# Thread.Sleep(20);
