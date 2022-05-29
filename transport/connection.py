class Connection:
    @staticmethod
    def connect(address, port):
        pass

    def _run_network(self):
        pass

    def on_event(self, event):
        pass
    
    def send(self, data: bytes):
        pass
    
    def recv(self, buffer_size: int) -> bytes:
        pass

    def close(self):
        pass
