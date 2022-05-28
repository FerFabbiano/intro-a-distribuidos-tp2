
from threading import Thread

from FSConnection import FSConnection
from transport.protocol import Protocol


OP_CODE_SIZE = 1

LISTEN_TO = 5

class FSServer:
    def __init__(self, host, port):

        self.keep_running = True
        self.connections = {}
        self.protocol = Protocol(host, port)
        self.protocol_thread = Thread(target=self.protocol.run)
        self.protocol_thread.start()

    def run(self):
        print("[ INFO ] - Running server")

        while self.keep_running:
            print("[ INFO ] - Waiting New Connections")

            connection_data = self.protocol.get_new_connection()

            if(connection_data is None):
                return

            data, address = connection_data
            print("[ INFO ] - Have New Connection from ", str(address))

            if not self.connections.get(address):
                self.connections[address] = FSConnection(self.protocol, data)

    def stop_running(self):

        self.keep_running = False
        self.protocol.close()
        self.protocol_thread.join()

        for _, value in self.connections.items():
            value.close()
