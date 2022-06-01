import time

from .rdp import RdpController, StopAndWaitRdpController
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
        import threading
        self = Connection(controller)
        threading.Thread(target=self._run_timers).start()
        threading.Thread(target=self._run_network).start()
        return self
    
    def _run_timers(self):
        while self.is_alive():
            time.sleep(0.010)
            self.on_tick(time.time())

    def _run_network(self):
        while self.is_alive():
            msg, client_address = self._controller._network.socket.recvfrom(65536)
            # validar client_address
            segment = Segment.from_datagram(msg)
            if not segment.is_checksum_correct():
                print("[Connection.run_network] Segment with invalid checksum: ", segment)
                continue
            print(segment)

            if segment.opcode == Opcode.NewConnectionReply:    
                self.on_new_connection_reply(segment)
            elif segment.opcode == Opcode.Data:
                self.on_data_received(segment)
            elif segment.opcode == Opcode.Ack:
                self.on_ack_received(segment)
            elif segment.opcode == Opcode.Close:
                self.on_close(segment)
            else:
                print("[Listener.run_network] Unknown opcode: ", segment)
    
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