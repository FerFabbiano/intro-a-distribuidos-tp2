import time
import threading
import queue
import logging
from .rdp_controller import RdpController
from transport.segment import Segment, Opcode

TIME_TO_CONSIDER_LOST_SECS = 0.3
MAX_RETRIES = 10
SEND_WINDOW_SIZE = 128
RECV_WINDOW_SIZE = 2 * SEND_WINDOW_SIZE


class SelectiveRepeatRdpController(RdpController):
    def __init__(self, raw_connection):
        self._mss = 500

        self._send_window = []
        self._swnd_size = SEND_WINDOW_SIZE  # Max size for _send_window
        self._acks_received = set()
        self._send_sequence_number = 1
        
        self._rwnd_size = RECV_WINDOW_SIZE  # Max size of _recv_window
        self._recv_window = [None] * self._rwnd_size
        self._recv_sequence_number = 0

        self._recv_queue = queue.Queue()
        self._network = raw_connection
        self._connection_dead = False
        self.lock = threading.Lock()
        self._send_window_cv = threading.Condition(threading.Lock())

    def do_active_handshake(self):
        self.send_segment(Segment(Opcode.NewConnection))

        # Wait for ACK to come and clear the cwnd
        self._flush_flight_window()

    def do_passive_handshake(self, welcome_segment):
        self._recv_sequence_number = welcome_segment.sequence_number
        self._send_ack(welcome_segment.sequence_number)

    def on_tick(self, current_time):
        with self.lock:
            for segment in self._send_window:
                if segment.creation_time + TIME_TO_CONSIDER_LOST_SECS < time.time():
                    self._on_packet_lost(segment)

    def on_data_received(self, segment):
        with self.lock:
            rwnd_offset = segment.sequence_number - self._recv_sequence_number - 1
            if (0 <= rwnd_offset < self._rwnd_size) and self._recv_window[rwnd_offset] is None:
                self._recv_window[rwnd_offset] = segment
            
            if rwnd_offset < self._rwnd_size:
                self._send_ack(segment.sequence_number)
            
            self._update_recv_window()
    
    def _update_recv_window(self):
        window_offset = 0
        for segment in self._recv_window:
            if not segment:
                break
            
            window_offset += 1
        
        if window_offset > 0:
            received_segments = self._recv_window[:window_offset]
            self._recv_window = self._recv_window[window_offset:] + [None] * window_offset
            self._recv_sequence_number = received_segments[-1].sequence_number
            for segment in received_segments:
                print(f'Putting segment {segment}')
                self._recv_queue.put(segment)

    def on_ack_received(self, ack):
        with self.lock:
            if not self._send_window:
                print('[SR.on_ack] Got ACK but no in-flight segments')
                return
            
            # The first seqnum in our flight window is the window_base, 
            # because the flight window is sorted by seqnum.
            window_base = self._send_window[0].sequence_number

            if ack.sequence_number < window_base:
                print(f'[SR.on_ack] Got ACK for old packet {ack.sequence_number=}, window_base={window_base}')
                return
            
            if window_base <= ack.sequence_number < window_base + len(self._send_window):
                # Got new ack, add it to the set
                self._acks_received.add(ack.sequence_number)
            
            if ack.sequence_number >= window_base + len(self._send_window):
                print(f'[SR.on_ack] Got ACK from the future?? {ack.sequence_number=}, window_limit={window_base+len(self._send_window)}')
            
        self._update_send_window()
    
    def _update_send_window(self):
        # Global mutex must not be locked!!!
        window_offset = 0
        for segment in self._send_window:
            if segment.sequence_number not in self._acks_received:
                break
            
            self._acks_received.remove(segment.sequence_number)
            window_offset += 1
        
        if window_offset == 0:
            return

        with self._send_window_cv:
            with self.lock:
                self._send_window = self._send_window[window_offset:]
            self._send_window_cv.notify()

    def send_segment(self, segment: Segment):
        """
        Blocks until the segment is sent.

        This method will update the segment's sequence number
        to the correct value.
        """
        with self._send_window_cv:
            while len(self._send_window) >= self._swnd_size:
                self._send_window_cv.wait()
            # Push segment to the network
            with self.lock:
                assert len(
                    segment.payload) <= self.mss, f'Segment size must not be greater than {self.mss}'
                segment.sequence_number = self._send_sequence_number
                self._send_sequence_number += 1
                self._network.send_segment(segment)
                self._send_window.append(segment)

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
        logging.info("[RDP.on_loss] {}".format(segment_lost))
        if segment_lost.retries >= MAX_RETRIES:
            self._send_window = []
            self._connection_dead = True
            raise Exception(f"Segment {segment_lost} re-sent more than {MAX_RETRIES} times. Connection dead")
        else:
            self._network.send_segment(segment_lost)
            segment_lost.creation_time = time.time()
            segment_lost.retries += 1

    def _send_ack(self, ack_number):
        ack = Segment(Opcode.Ack)
        ack.sequence_number = ack_number
        self._network.send_segment(ack)

    def _flush_flight_window(self):
        with self._send_window_cv:
            while self._send_window:
                self._send_window_cv.wait()

    def close(self):
        self._flush_flight_window()
