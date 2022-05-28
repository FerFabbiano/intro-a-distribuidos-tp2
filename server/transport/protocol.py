from queue import Queue
import socket

BUFFER_SIZE = 508

ACK = b"OK"


class Protocol():
    def __init__(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((host, port))
        self.keep_running = True
        self.new_connections = Queue()

    def run(self):
        while(self.keep_running):
            print("[ INFO IN PROTOCL ] - Waiting new message")

            try:
                msg, clientAddress = self.socket.recvfrom(BUFFER_SIZE)

                # Parse new connections.
                if chr(msg[0]) == 'N':
                    print("[ INFO IN NEW CONNECTION ] - ", msg[1:])
                    self.new_connections.put((msg[1:], clientAddress))
            except Exception as e:
                print("[ INFO ] - Shutting down server ", e)

        print("[ INFO IN PROTOCOL ] - Closing")

        # if msg[0] == 'C':
        #     self.
        # if not self.buffers[clientAddress]:
        #     self.buffers[clientAddress] = []

        # self.buffers[clientAddress].append(msg)

    def get_new_connection(self):
        print("[ INFO IN PROTOCOL ] - Waiting New Connections")

        return self.new_connections.get()

    def send_ack(self, address):
        self.socket.sendto(ACK, address)

    def send_bytes(self, address, data):
        sentBytes = self.socket.sendto(data, address)
        print("[ INFO ] - Enviamos: ", str(sentBytes))

        # originIP = "IP ORIGEN"
        # originPORT = "PUERTO ORIGEN"
        # recvBytes = 10
        # payload = "lalala"

        return None

    def close(self):
        self.keep_running = False
        print("[ INFO ] - Closing socket connections")
        self.socket.close()
        self.new_connections.put(())
        self.new_connections.join()
