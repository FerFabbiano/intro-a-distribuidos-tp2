from fs_connection import FSConnection
from transport.listener import Listener


OP_CODE_SIZE = 1

LISTEN_TO = 5


class FSServer:
    def __init__(self, host, port):

        self.keep_running = True
        self.connections = {}
        self.listener = Listener(host, port)

    def run(self):
        print("[ INFO ] - Running server")

        while self.keep_running:
            print("[ INFO ] - Waiting New Connections")

            connection_data = self.listener.get_new_connection()

            if(connection_data is None):
                return

            data, address = connection_data
            print("[ INFO ] - Have New Connection from ", str(address))

            if not self.connections.get(address):
                self.connections[address] = FSConnection(self.protocol, data)

    def stop(self):

        self.keep_running = False
        self.listener.close()

        for _, value in self.connections.items():
            value.close()
