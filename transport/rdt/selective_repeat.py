import time
import threading
import queue
import logging
from .rdt_controller import RdtController
from transport.segment import Segment, Opcode

TIME_TO_CONSIDER_LOST_SECS = 0.5
MAX_RETRIES = 10
SEND_WINDOW_SIZE = 64
RECV_WINDOW_SIZE = 2 * SEND_WINDOW_SIZE


class SelectiveRepeatRdtController(RdtController):
    def __init__(self, raw_connection):
        self._mss = 500

        # state as sender
        self._send_window = []
        self._swnd_size = SEND_WINDOW_SIZE  # Max size for _send_window
        self._acks_received = set()
        self._send_sequence_number = 1

        # state as receiver
        self._rwnd_size = RECV_WINDOW_SIZE  # Max size of _recv_window
        self._recv_window = [None] * self._rwnd_size
        self._recv_sequence_number = 0

        # state for upper layer / concurrency
        self._recv_queue = queue.Queue()
        self._network = raw_connection
        self._connection_dead = False
        self.lock = threading.Lock()
        self._send_window_cv = threading.Condition(threading.Lock())

        self._closing = False
        self._remote_end_closed = False

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
            # The receive window always has _rwnd_size items, which could be an instance of
            # Segment or None.

            # find offset of segment inside recv window
            rwnd_offset = segment.sequence_number - self._recv_sequence_number - 1
            if (0 <= rwnd_offset < self._rwnd_size) and self._recv_window[rwnd_offset] is None:
                # If it is inside the window, and we haven't received it yet, store it in the
                # recv window.
                self._recv_window[rwnd_offset] = segment

            # If the offset of the segment received does not go beyond the size of the window,
            # we need to send an ACK for it.
            # If 0 <= rwnd_offset < rwnd_size, then we have stored it in the recv_window
            # if rwnd_offset < 0, then a previous ACK may have been lost.
            if rwnd_offset < self._rwnd_size:
                self._send_ack(segment.sequence_number)

            # Once we stored the new segment and send the corresponding ACK, we need to see
            # if we can increment the 'recv window base'.
            self._update_recv_window()

    def _update_recv_window(self):
        """
        Checks if it can push any segment from the receive window to the upper
        layer.
        """
        window_offset = 0
        for segment in self._recv_window:
            # The receive window is sorted by sequence number, so we increment the offset
            # until we find a missing segment in the window.
            if not segment:
                break

            window_offset += 1

        if window_offset > 0:  # If we can push at least one segment to the upper layer...
            # Remove the segments from the window...
            received_segments = self._recv_window[:window_offset]
            self._recv_window = self._recv_window[window_offset:] + [
                None] * window_offset

            # update the 'recv window base'...
            self._recv_sequence_number = received_segments[-1].sequence_number
            for segment in received_segments:
                # and send the segments to the upper layer.
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
                print(
                    f'[SR.on_ack] Got ACK for old packet {ack.sequence_number=}, window_base={window_base}')
                return

            if window_base <= ack.sequence_number < window_base + len(self._send_window):
                # Got new ack, add it to the set
                self._acks_received.add(ack.sequence_number)

            if ack.sequence_number >= window_base + len(self._send_window):
                print(
                    f'[SR.on_ack] Got ACK from the future?? {ack.sequence_number=}, window_limit={window_base+len(self._send_window)}')

        self._update_send_window()
    
    def on_close_received(self, segment):
        """
        Called by the protocol when a CLOSE has been received.
        """
        print('[SR.on_close_received]')
        self._remote_end_closed = True
        self._send_ack(segment.sequence_number)

    def _update_send_window(self):
        """
        Checks what ACKs have been received and updates the send window 
        accordingly.

        Note that the global instance lock must not be held when calling
        this method, otherwise a deadlock may occur.s
        """
        with self.lock:
            window_offset = 0
            for segment in self._send_window:
                # The send window is sorted by seqnum. We increment the
                # window_offset as long as we have the ACK for that segment.
                if segment.sequence_number not in self._acks_received:
                    break

                # "Consume" the ACK
                self._acks_received.remove(segment.sequence_number)
                window_offset += 1

            if window_offset == 0:
                return

            # Remove ACK'd segments from the send window...
            self._send_window = self._send_window[window_offset:]

        # and notify that there was a change in the window
        with self._send_window_cv:
            self._send_window_cv.notify()

    def send_segment(self, segment: Segment):
        """
        Blocks until the segment is sent.

        This method will update the segment's sequence number
        to the correct value.
        """
        if self._closing:
            raise Exception("Trying to send a segment after closing the connection")
        
        assert len(segment.payload) <= self.mss, \
            f'Segment size must not be greater than {self.mss}'

        with self._send_window_cv:
            while len(self._send_window) >= self._swnd_size:
                self._send_window_cv.wait()

            with self.lock:
                segment.sequence_number = self._send_sequence_number
                self._send_sequence_number += 1
                self._network.send_segment(segment)
                self._send_window.append(segment)
        return True

    def recv_segment(self) -> Segment:
        """
        Blocks until a segment is available to be read.
        """
        if self._recv_queue.empty() and self._remote_end_closed:
            return
        
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
            raise Exception(
                f"Segment {segment_lost} re-sent more than {MAX_RETRIES} times. Connection dead")
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
        if not self._closing:
            self._flush_flight_window()
            self.send_segment(Segment(Opcode.Close))
            self._flush_flight_window()
            self._closing = True
            # "Time wait"
            time.sleep(1.5 * TIME_TO_CONSIDER_LOST_SECS)
