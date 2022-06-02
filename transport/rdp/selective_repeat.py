import queue
import threading

from transport.rdp import RdpController
from transport.segment import Segment, Opcode


class SelectiveRepeatRdpController(RdpController):
    def __init__(self, raw_connection):
        self._mss = 500
        # tenemos mas de uno in_flight
        # self._in_flight = None
        self._sequence_number = 1
        # self._recv_sequence_number = 0
        self._recv_queue = queue.Queue()
        self._network = raw_connection
        # self._connection_dead = False
        self.lock = threading.Lock()
        # self._in_flight_cv = threading.Condition(threading.Lock())
        self.recv_window_base = 0
        # SACADO DEL LIBRO
        # A problem at the end of the chapter asks you to show that the window size must be less than
        # or equal to half the size of the sequence number space for SR protocols.
        self.recv_window_size = 4
        self.recv_buffer = {}

    def do_active_handshake(self):
        """
        Starts the handshake of an active (client-to-server) connection.
        """
        pass

    # respuesta de handshake
    def do_passive_handshake(self, welcome_segment):
        """
        Responds to a handshake of a passive (server-to-client) connection.
        """
        pass

    def on_tick(self, current_time):
        """
        Called by the protocol in regular periods of time
        """
        pass

    def on_data_received(self, segment):
        """
        Called by the protocol when a new segment containing data has 
        been received.
        """
        with self.lock:
            if self.recv_window_base <= segment.sequence_number <= self.recv_window_base + self.recv_window_size - 1:
                # correctly received, new packet

                # send individual ack for this packet, no matter if disordered
                self._send_ack(segment.sequence_number)

                if segment.sequence_number != self.recv_window_base:
                    # it arrived disordered,store it in buffer
                    self.recv_buffer[segment.sequence_number] = segment
                else:
                    # received the packet in order
                    # send this packet and all consecutives in buffer
                    self._recv_queue.put(segment)
                    send = True
                    i = 1
                    while send:
                        if self.recv_window_base + i in self.recv_buffer:
                            self._recv_queue.put(self.recv_buffer.pop(self.recv_window_base + i))
                            i += 1
                        else:
                            send = False
                    # forward window base by number of packets delivered to upper layer
                    self.recv_window_base += i

            if self.recv_window_base - self.recv_window_size <= segment.sequence_number <= self.recv_window_base - 1:
                # ack for this packet may have not reached the sender, reacknowledge packet
                self._send_ack(segment.sequence_number)

    def on_ack_received(self, segment):
        """
        Called by the protocol when a new ACK has been received.
        """
        pass

    def send_segment(self, segment: Segment):
        """
        Blocks until the segment is sent.

        This method will update the segment's sequence number
        to the correct value.
        """
        pass

    def recv_segment(self) -> Segment:
        """
        Blocks until a segment is avaiable to be read.
        """

    @property
    def mss(self):
        """
        Returns the maximum size of a segment's payload, in bytes.

        This property is guaranteed to be constant for the whole
        lifetime of the RdpController's instance.
        """
        pass

    def is_alive(self):
        """
        Returns True if the connection is still alive.
        """
        pass

    def _send_ack(self, ack_number):
        ack = Segment(Opcode.Ack)
        ack.sequence_number = ack_number
        self._network.send_segment(ack)
