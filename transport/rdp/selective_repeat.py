import queue
import threading
import time
import logging
from transport.rdp import RdpController
from transport.segment import Segment, Opcode

TIME_TO_CONSIDER_LOST_SECS = 10
MAX_RETRIES = 3
SEND_WINDOW_SIZE = 4
RECV_WINDOW_SIZE = 4


class SelectiveRepeatRdpController(RdpController):
    def __init__(self, raw_connection):
        self._mss = 500
        self._in_flight = {}
        self._sequence_number = 1
        # self._recv_sequence_number = 0
        self._recv_queue = queue.Queue()
        self._network = raw_connection
        self._connection_dead = False
        self.lock = threading.Lock()
        self._send_window_cv = threading.Condition(threading.Lock())
        # self._in_flight_cv = threading.Condition(threading.Lock())
        self._recv_window_base = self._sequence_number
        # SACADO DEL LIBRO
        # A problem at the end of the chapter asks you to show that the window size must be less than
        # or equal to half the size of the sequence number space for SR protocols.
        self._recv_buffer = {}
        self._send_window_base = self._sequence_number

    def do_active_handshake(self):
        """
        Starts the handshake of an active (client-to-server) connection.
        """
        # Se que entra en la ventana entonces se que el seq number que le asiganara al paquete
        # de bienvenida es el self._sequence_number

        # with self._send_window_cv:
        # send_window_end = self._send_window_base + SEND_WINDOW_SIZE - 1
        # while not (self._send_window_base <= self._sequence_number <= send_window_end):
        # the seq number is not within the send window, the packet has to wait
        # self._send_window_cv.wait()
        seg = Segment(Opcode.NewConnection)
        self.send_segment(seg)

        # Wait for ACK to come and clear the cwnd
        with self._send_window_cv:
            while seg.sequence_number in self._in_flight:
                # no llego el ack
                self._send_window_cv.wait()

        # Since connection was not established yet, we should check if we've got an
        # ACK of if we should consider the connection as dead.
        if self._connection_dead:
            raise Exception('Could not establish a connection to the server')

    # respuesta de handshake
    def do_passive_handshake(self, welcome_segment):
        """
        Responds to a handshake of a passive (server-to-client) connection.
        """
        self._recv_window_base += 1
        self._send_ack(welcome_segment.sequence_number)

    def on_tick(self, current_time):
        """
        Called by the protocol in regular periods of time
        """
        with self.lock:
            for seq_number in list(self._in_flight):
                if self._in_flight[seq_number].creation_time + TIME_TO_CONSIDER_LOST_SECS < time.time():
                    segment_lost = self._in_flight.pop(seq_number)
                    self._on_packet_lost(segment_lost)

    def on_data_received(self, segment):
        """
        Called by the protocol when a new segment containing data has
        been received.
        """

        with self.lock:

            if self._recv_window_base <= segment.sequence_number <= self._recv_window_base + RECV_WINDOW_SIZE - 1:

                # correctly received, new packet

                # send individual ack for this packet, no matter if disordered
                self._send_ack(segment.sequence_number)

                if segment.sequence_number != self._recv_window_base:
                    # it arrived disordered,store it in buffer
                    self._recv_buffer[segment.sequence_number] = segment
                else:
                    # received the packet in order
                    # send this packet and all consecutives in buffer
                    self._recv_queue.put(segment)
                    send = True
                    i = 1
                    while send:
                        if self._recv_window_base + i in self._recv_buffer:
                            self._recv_queue.put(self._recv_buffer.pop(
                                self._recv_window_base + i))
                            i += 1
                        else:
                            send = False
                    # forward window base by number of packets delivered to upper layer
                    self._recv_window_base += i

            if self._recv_window_base - RECV_WINDOW_SIZE <= segment.sequence_number <= self._recv_window_base - 1:
                # ack for this packet may have not reached the sender, reacknowledge packet
                self._send_ack(segment.sequence_number)

    def on_ack_received(self, segment):
        """
        Called by the protocol when a new ACK has been received.
        """
        with self.lock:
            for seq_number in list(self._in_flight):
                if seq_number == segment.sequence_number:
                    logging.debug("[RDP.on_ack] ACK MATCHES")
                    # Segment was received, no longer in flight
                    self._in_flight.pop(seq_number)
                    break

            # print("[RDP.on_ack] ACK DOESN'T MATCH")
            if segment.sequence_number == self._send_window_base:
                # move send window base to the lowest unacknowledged sequence number
                with self._send_window_cv:
                    if len(self._in_flight) > 0:
                        self._send_window_base = min(self._in_flight.keys())
                    self._send_window_cv.notify()

    def send_segment(self, segment: Segment):
        """
        Blocks until the segment is sent.

        This method will update the segment's sequence number
        to the correct value.
        """
        with self._send_window_cv:
            send_window_end = self._send_window_base + self._send_window_size - 1
            while not (self._send_window_base <= self._sequence_number <= send_window_end):
                # the seq number is not within the send window, the packet has to wait
                self._send_window_cv.wait()

            with self.lock:
                assert len(
                    segment.payload) <= self.mss, f'Segment size must not be greater than {self.mss}'
                segment.sequence_number = self._sequence_number
                self._sequence_number += 1
                self._network.send_segment(segment)
                self._in_flight[segment.sequence_number] = segment

    def recv_segment(self) -> Segment:
        """
        Blocks until a segment is avaiable to be read.
        """
        return self._recv_queue.get()

    @property
    def mss(self):
        """
        Returns the maximum size of a segment's payload, in bytes.

        This property is guaranteed to be constant for the whole
        lifetime of the RdpController's instance.
        """
        return self._mss

    def is_alive(self):
        """
        Returns True if the connection is still alive.
        """
        pass

    def _on_packet_lost(self, segment_lost):
        logging.debug("[RDP.on_loss] {}".format(segment_lost))
        if segment_lost.retries >= MAX_RETRIES:
            self._connection_dead = True
            with self._send_window_cv:
                self._send_window_cv.notify()
        else:
            self._network.send_segment(segment_lost)
            segment_lost.creation_time = time.time()
            segment_lost.retries += 1
            self._in_flight[segment_lost.sequence_number] = segment_lost

    def _send_ack(self, ack_number):
        ack = Segment(Opcode.Ack)
        ack.sequence_number = ack_number
        self._network.send_segment(ack)
