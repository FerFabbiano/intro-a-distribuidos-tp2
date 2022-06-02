"Mock Connection Object"

import socket
import logging


class Connection():
    def __init__(self, address, tcpsocket):
        logging.debug("[ PC ] - New Protocol Connection")
        self.__socket = tcpsocket
        self.__address = address

    def push_message(self, message):
        self.messages

    def __repr__(self):
        return str(self.__address)

    @property
    def attr(self):
        return self.__attr

    def address(self):
        self.__address

    @staticmethod
    def connect(address, port, controller=None):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((address, port))

        return Connection((address, port), sock)

    def send(self, data):
        return self.__socket.send(data)

    def recv(self, buffer_size):
        return self.__socket.recv(buffer_size)

    def recv_exact(self, buffer_size: int) -> bytes:
        buffer = bytes()
        while len(buffer) < buffer_size:
            buffer += self.recv(buffer_size - len(buffer))
        return buffer

    def close(self):
        self.__socket.close()
