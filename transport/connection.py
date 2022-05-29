class Connection:
    def __init__(self, controller: RdpController):
        self._controller = controller
    
    @property
    def controller(self):
        return self._controller
   
    @staticmethod
    def connect(address, port):
        pass
    
    def send(self, data: bytes):
        pass
    
    def recv(self, buffer_size: int) -> bytes:
        pass

    def close(self):
        pass
