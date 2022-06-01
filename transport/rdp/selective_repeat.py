class SelectiveRepeatRdpController:
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

    def pop_recv_queue(self):
        """
        Waits until the next segment in the sequence arrives and returns it
        """
        pass