from abc import abstractmethod
import socket


CHUNK_SIZE = 1024


class ByteStream:
    @abstractmethod
    def send_bytes():
        pass

    @abstractmethod
    def recv_bytes():
        pass

    @abstractmethod
    def close():
        pass


class ByteStreamTcp(ByteStream):
    def __init__(self, socket):
        self.socket = socket

    def send_bytes(self, data):
        self.socket.send(data)  # ver si envia TODA la data o una parte

    def recv_bytes(self, quantity):
        return self.socket.recv(
            quantity
        )  # ver si recibe exactamente quantity bytes como maximo qty bytes.

    def close(self):
        self.socket.close()


class ByteStreamTcpClient(ByteStreamTcp):
    @staticmethod
    def connect(host, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        return ByteStreamTcp(s)


LISTEN_TO = 5


class ByteStreamTcpServer:
    def __init__(self, host, port):
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = host
        self.port = port
        self.listener.bind((host, port))
        self.listener.listen(LISTEN_TO)
        self.keep_running = True

    def run(self):
        print("[ INFO ] - Running server")

        while self.keep_running:
            try:
                peer_socket, addr = self.listener.accept()
                connection = ByteStreamTcp(peer_socket)
            except ConnectionAbortedError:
                print("[ INFO ] - Shutting down server")
                continue

            while True:
                data = connection.recv_bytes(CHUNK_SIZE)

                if not data:
                    break

                print("[ INFO ] - Got " + str(data) + " from client")

    def stop_running(self):
        self.keep_running = False
        self.listener.close()
