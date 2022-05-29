class RdpController:
    def send_welcome_segment(self):
        """
        Sends a welcome segment for a new connection
        """
        pass
    
    def on_new_connection_reply(self, segment):
        """
        A NewConnectionReply has been received.
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
        pass
    
    def on_ack_received(self, segment):
        """
        Called by the protocol when a new ACK has been received.
        """
        pass

    def try_send_segment(self, data: bytes) -> bool:
        """
        Tries to create a new segment and push it to the network.

        data: Payload to send. len(data) < self.mss. 

        Returns:
            True if the segment was succesfully sent to the network
            False if the congestion window is full / there are too
                  many segments in flight.
        """
        pass

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

import time
from transport.segment import Segment, Opcode

TIME_TO_CONSIDER_LOST_SECS = 0.250
MAX_RETRIES = 3

class StopAndWaitRdpController(RdpController):
    def __init__(self, network):
        self._mss = 500
        self._in_flight = None
        self._sequence_number = 1
        self._recv_sequence_number = 0
        self._recv_queue = []
        self._network = network
        self._connection_dead = False

    def on_new_connection_reply(self, segment):
        self.send_ack(1)

    @property
    def mss(self):
        return self._mss
    
    def is_alive(self):
        return not self._connection_dead
    
    def try_send_segment(self, segment: Segment) -> bool:
        assert len(segment.payload) <= self.mss, f'Segment size must not be greater than {self.mss}'
        if self._in_flight is not None:
            return False  # No more space in window
        
        segment.sequence_number = self._sequence_number
        self._network.send_segment(segment)
        self._in_flight = segment
        return True

    def on_tick(self, current_time):
        if self._in_flight is not None:
            if self._in_flight.creation_time + TIME_TO_CONSIDER_LOST_SECS > time.time():
                # packet lost
                segment_lost = self._in_flight
                self._in_flight = None
                self.on_packet_lost(segment_lost)
    
    def on_data_received(self, segment):
        # Update our _recv_sequence_number
        if segment.sequence_number == self._recv_sequence_number + 1:
            self._recv_sequence_number += 1
            self._recv_queue.append(segment)
        
        # Send ACK
        self.send_ack(self._recv_sequence_number)

    def on_ack_received(self, segment):
        ack_number = struct.unpack("!I", segment.payload)
        if self._sequence_number == ack_number:
            self._in_flight = None  # Segment was received by the other end

    def on_packet_lost(self, segment_lost):
        if segment_lost.retries >= MAX_RETRIES:
            self._connection_dead = True
        else:
            self._network.send_segment(segment_lost)
            segment_lost.creation_time = time.time()
            segment_lost.retries += 1
            self._in_flight = segment_lost
    
    def send_ack(self, ack_number):
        ack = Segment(Opcode.Ack, bytes())
        ack.sequence_number = ack_number
        self._network.send_segment(ack)

    def pop_recv_queue(self):
        while not self._recv_queue:
            time.sleep(0.010)
        
        return self._recv_queue.pop(0)