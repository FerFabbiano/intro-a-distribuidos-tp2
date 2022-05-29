from server.fs_connection import FSConnection
from transport_tcp.listener import Listener


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

            new_connection = self.listener.get_new_connection()

            if new_connection is None:
                return

            print("[ INFO ] - Have New Connection from ", str(new_connection))

            # If we don't have a client connection with that specific address
            # We create one
            if not self.connections.get(new_connection.address):
                self.connections[new_connection.address] = FSConnection(new_connection)

    def stop(self):

        self.keep_running = False
        self.listener.close()

        for _, value in self.connections.items():
            value.close()
