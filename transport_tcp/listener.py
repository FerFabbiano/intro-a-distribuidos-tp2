from queue import Queue
import socket
from threading import Thread
import logging
from .connection import Connection

BUFFER_SIZE = 508

ACK = b"OK"


class Listener():
    def __init__(self, host, port):
        # Binding TCP - This is temporary.
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((host, port))
        self.socket.listen(5)

        self.keep_running = True
        self.new_connections = Queue()
        self.thread = Thread(target=self.run)
        self.thread.start()

    def run(self):
        while(self.keep_running):
            logging.debug("[ INFO IN PROTOCL ] - Waiting new message")

            try:
                (clientsocket, address) = self.socket.accept()
                self.new_connections.put(Connection(address, clientsocket))
            except Exception:
                logging.debug("[ INFO PROTOCOL ] - Closing Socket Connection ")

    def get_new_connection(self):
        return self.new_connections.get()

    def send_ack(self, address):
        self.socket.sendto(ACK, address)

    def close(self):
        logging.debug(
            "[ INFO PROTOCOL ] - Starting Closing protocol connection")

        self.keep_running = False
        self.socket.close()
        self.new_connections.put(None)
        self.thread.join()

        logging.debug(
            "[ INFO PROTOCOL ] - Finishing Closing protocol connection")
