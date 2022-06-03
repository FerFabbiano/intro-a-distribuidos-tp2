import time

from .segment import Segment, Opcode
import logging
NETWORK_TICK_SECONDS = 0.010


class Connection:
    @staticmethod
    def connect(host, port, controller=None):
        from .active_connection import ActiveConnection
        return ActiveConnection(host, port, controller)

    def __init__(self, address, controller):
        self._controller = controller
        self._address = address

    def on_tick(self):
        """
        Timer event
        """
        self._controller.on_tick(time.time())

    def on_segment_received(self, segment, _):
        """
        Forwards a network event to the rdt controller
        """
        if segment.opcode == Opcode.NewConnection:
            self._controller.do_passive_handshake(segment)
        elif segment.opcode == Opcode.Data:
            self._controller.on_data_received(segment)
        elif segment.opcode == Opcode.Ack:
            self._controller.on_ack_received(segment)
        elif segment.opcode == Opcode.Close:
            self._controller.on_close_received(segment)
        else:
            logging.debug("[Connection.on_segment_received] Unknown opcode ")

    def send(self, data: bytes) -> int:
        for i in range(0, len(data), self._controller.mss):
            if not self._controller.send_segment(
                Segment(Opcode.Data, data[i:(i + self._controller.mss)])):
                return i
        return len(data)

    def recv(self, buffer_size: int) -> bytes:
        if not self._recv_buffer:
            segment = self._controller.recv_segment()
            if not segment:
                return bytes()
            self._recv_buffer += segment.payload
        data = self._recv_buffer[:buffer_size]
        self._recv_buffer = self._recv_buffer[buffer_size:]
        return data

    def recv_exact(self, buffer_size: int) -> bytes:
        buffer = bytes()
        while len(buffer) < buffer_size:
            buffer += self.recv(buffer_size - len(buffer))
        return buffer

    def close(self):
        print('CLOSING RDT CONNECTION')
        self._controller.close()
        print('RDT CONNECTION CLOSED')

    def is_alive(self):
        return self._controller.is_alive()

    @property
    def address(self):
        return self._address
