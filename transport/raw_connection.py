import socket

class RawConnection:
    @staticmethod
    def connect(host, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        return RawConnection(s, (host, port))

    def __init__(self, socket, destination_address):
        self.socket = socket
        self.destination_address = destination_address
    
    def send_segment(self, segment):
        self.socket.sendto(segment.serialize(), self.destination_address)
