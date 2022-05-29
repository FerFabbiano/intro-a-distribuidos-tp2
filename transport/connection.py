from .rdp.rdp_controller import RdpController, StopAndWaitRdpController
from .raw_connection import RawConnection
from transport.segment import Segment, Opcode

class Connection:
    def __init__(self, controller: RdpController):
        self._controller = controller
    
    def on_new_connection_reply(self, segment):
        self._controller.on_new_connection_reply(segment)
    
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
   
    def on_close(self):
        pass

    @staticmethod
    def connect(host, port):
        raw_connection = RawConnection.connect(host, port)
        controller = StopAndWaitRdpController(raw_connection)
        assert controller.try_send_segment(Segment(Opcode.NewConnection, bytes()))
        data, client_address = raw_connection.socket.recvfrom(65536)
        ack = Segment.from_datagram(data)
        assert (host, port) == client_address and data.opcode == Opcode.Ack
        return Connection(controller)
    
    def send(self, data: bytes) -> int:
        part = data[0:self._controller.mss]
        segment = Segment(Opcode.Data, part)
        while not self._controller.try_send_segment(segment):
            time.sleep(0.010)
        return len(part)
    
    def recv(self, buffer_size: int) -> bytes:
        return self._controller.pop_recv_queue().payload

    def close(self):
        pass

    def is_alive(self):
        return self._controller.is_alive()