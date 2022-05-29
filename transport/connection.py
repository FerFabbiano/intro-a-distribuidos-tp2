class Connection:
    def __init__(self, controller: RdpController):
        self._controller = controller
    
    def on_tick(self, current_time):
        """
        Called by the protocol in regular periods of time
        """
        self._controller.on_tick(current_time)
    
    def on_data_received(self, segment):
        """
        Called by the protocol when a new segment containing data has 
        been received.
        """
        self._controller.on_data_received(segment)
    
    def on_ack_received(self, segment):
        """
        Called by the protocol when a new ACK has been received.
        """
        self._controller.on_ack_received(segment)
   
    @staticmethod
    def connect(address, port):
        pass
    
    def send(self, data: bytes):
        pass
    
    def recv(self, buffer_size: int) -> bytes:
        pass

    def close(self):
        pass
