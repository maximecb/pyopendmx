
import socket
import threading

# Loop to listen to clients who want to subscribe
def listen_loop(server):
    print("Starting beat server listening loop")

    while True:
        try:
            # buffer size is 1024 bytes
            data, addr = server.sock.recvfrom(1024)
            print("received message: {}".format(data))
            print("client addr: {}".format(addr))

            # Add the address to the listener set
            server.subs.add(addr)
        except:
            "stopping server"
            break

class BeatServer:
    """
    Simple UDP server to notify subscribers that a beat happened
    """

    def __init__(self, port_no = 7777):
        self.port_no = 7777
        self.subs = set()

        # Create a listening socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(("0.0.0.0", port_no))

        # Start the listening thread
        t = threading.Thread(target=listen_loop, args=(self,))
        t.start()

    def stop(self):
        # This will stop the listening thread
        self.sock.close()

    # Notify subscribers that a beat was received
    def beat(self):
        for sub_addr in self.subs:
            #print('notifying sub {}', sub_addr)
            self.sock.sendto(b"beat!", sub_addr)
