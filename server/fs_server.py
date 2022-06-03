import os
from server.fs_connection import FSConnection
from transport.listener import Listener
import logging


class FSServer:
    def __init__(self, host, port, baseFsFolder):

        self.keep_running = True
        self.connections = {}
        self.baseFsFolder = baseFsFolder

        if not os.path.exists(baseFsFolder):
            os.makedirs(baseFsFolder)

        self.listener = Listener(host, port)

    def __clean_zombies(self):

        for keyAddress, fsConnection in self.connections.items():
            if fsConnection.is_dead:
                fsConnection.close()
                del self.connections[keyAddress]

    def run(self):
        logging.debug("[ INFO ] - Running server")

        while self.keep_running:
            logging.debug("[ INFO ] - Waiting New Connections")

            new_connection = self.listener.get_new_connection()

            if new_connection is None:
                return

            logging.debug("[ INFO ] - Have New Connection from %s",
                          str(new_connection))

            # If we don't have a client connection with that specific address
            # We create one
            if not self.connections.get(new_connection.address):
                self.connections[new_connection.address] = FSConnection(
                    new_connection, self.baseFsFolder)

            self.__clean_zombies()

    def stop(self):

        self.keep_running = False
        self.listener.close()

        for _, value in self.connections.items():
            value.close()
