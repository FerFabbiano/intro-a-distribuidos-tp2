"Mock Connection Object"


class Connection():
    def __init__(self, address, tcpsocket):
        print("[ PC ] - New Protocol Connection")
        self.socket = tcpsocket
        self.address = address

    def push_message(self, message):
        self.messages

    @staticmethod
    def connect(address, port, controller=None):
        pass

    def send(self, data: bytes):
        pass

    def recv(self, buffer_size: int) -> bytes:
        pass

    def close(self):
        pass
