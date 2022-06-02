import os
from server.config import BASE_FS_FOLDER
from server.fs_connection import FSConnection
from transport.listener import Listener
import logging


class FSServer:
    def __init__(self, host, port):

        self.keep_running = True
        self.connections = {}

        if not os.path.exists(BASE_FS_FOLDER):
            os.makedirs(BASE_FS_FOLDER)

        self.listener = Listener(host, port)

    def run(self):
        logging.info("[ INFO ] - Running server")

        while self.keep_running:
            logging.info("[ INFO ] - Waiting New Connections")

            new_connection = self.listener.get_new_connection()

            if new_connection is None:
                return

            logging.info("[ INFO ] - Have New Connection from %s",
                         str(new_connection))

            # If we don't have a client connection with that specific address
            # We create one
            if not self.connections.get(new_connection.address):
                self.connections[new_connection.address] = FSConnection(
                    new_connection)

    def stop(self):

        self.keep_running = False
        self.listener.close()

        for _, value in self.connections.items():
            value.close()
