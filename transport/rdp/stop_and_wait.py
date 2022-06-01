import time
import threading
import queue

from .rdp_controller import RdpController
from transport.segment import Segment, Opcode

TIME_TO_CONSIDER_LOST_SECS = 0.5
MAX_RETRIES = 3


class StopAndWaitRdpController(RdpController):
    def __init__(self, raw_connection):
        self._mss = 500
        self._in_flight = None
        self._sequence_number = 1
        self._recv_sequence_number = 0
        self._recv_queue = queue.Queue()
        self._network = raw_connection
        self._connection_dead = False
        self.lock = threading.Lock()
        self._in_flight_cv = threading.Condition(threading.Lock())

    def do_active_handshake(self):
        self.send_segment(Segment(Opcode.NewConnection))

        # Wait for ACK to come and clear the cwnd
        with self._in_flight_cv:
            while self._in_flight is not None:
                self._in_flight_cv.wait()
        
        # Since connection was not established yet, we should check if we've got an 
        # ACK of if we should consider the connection as dead.
        if self._connection_dead:
            raise Exception('Could not establish a connection to the server')
    
    def do_passive_handshake(self, welcome_segment):
        self._recv_sequence_number = welcome_segment.sequence_number
        self._send_ack(welcome_segment.sequence_number)

    def on_tick(self, current_time):
        with self.lock:
            if self._in_flight is not None:
                if self._in_flight.creation_time + TIME_TO_CONSIDER_LOST_SECS < time.time():
                    segment_lost = self._in_flight
                    self._in_flight = None
                    self._on_packet_lost(segment_lost)
    
    def on_data_received(self, segment):
        with self.lock:
            # Update our _recv_sequence_number
            if segment.sequence_number == self._recv_sequence_number + 1:
                self._recv_sequence_number += 1
                self._recv_queue.put(segment)
            
            # Send ACK
            self._send_ack(self._recv_sequence_number)

    def on_ack_received(self, segment):
        with self.lock:
            if self._sequence_number == segment.sequence_number + 1:
                print("[RDP.on_ack] ACK MATCHES")
                with self._in_flight_cv:
                    self._in_flight = None  # Segment was received by the other end
                    self._in_flight_cv.notify()
            else:
                print("[RDP.on_ack] ACK DOESN'T MATCH")

    def send_segment(self, segment: Segment):
        """
        Blocks until the segment is sent.

        This method will update the segment's sequence number
        to the correct value.
        """
        with self._in_flight_cv:
            while self._in_flight is not None:
                self._in_flight_cv.wait()
            # Push segment to the network
            with self.lock:
                assert len(segment.payload) <= self.mss, f'Segment size must not be greater than {self.mss}'
                segment.sequence_number = self._sequence_number
                self._sequence_number += 1
                self._network.send_segment(segment)
                self._in_flight = segment
    
    def recv_segment(self) -> Segment:
        """
        Blocks until a segment is available to be read.
        """
        return self._recv_queue.get()
    
    @property
    def mss(self):
        return self._mss
    
    def is_alive(self):
        return not self._connection_dead

    def _on_packet_lost(self, segment_lost):
        print("[RDP.on_loss]", segment_lost)
        if segment_lost.retries >= MAX_RETRIES:
            self._connection_dead = True
            with self._in_flight_cv:
                self._in_flight_cv.notify()
        else:
            self._network.send_segment(segment_lost)
            segment_lost.creation_time = time.time()
            segment_lost.retries += 1
            self._in_flight = segment_lost
    
    def _send_ack(self, ack_number):
        ack = Segment(Opcode.Ack)
        ack.sequence_number = ack_number
        self._network.send_segment(ack)
    