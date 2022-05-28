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
            except Exception:
                print("[ INFO PROTOCOL ] - Closing Socket Connection ")

    def get_new_connection(self):
        return self.new_connections.get()

    def send_ack(self, address):
        self.socket.sendto(ACK, address)

    def close(self):
        print("[ INFO PROTOCOL ] - Starting Closing protocol connection")

        self.keep_running = False
        self.socket.close()
        self.new_connections.put(None)

        print("[ INFO PROTOCOL ] - Finishing Closing protocol connection")
