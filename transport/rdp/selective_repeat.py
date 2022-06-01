class SelectiveRepeatRdpController:
    def do_active_handshake(self):
        """
        Starts the handshake of an active (client-to-server) connection.
        """
        pass

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
        pass

    def on_ack_received(self, segment):
        """
        Called by the protocol when a new ACK has been received.
        """
        pass

    def send_segment(self, segment):
        """
        Blocks until the segment is sent.

        This method will update the segment's sequence number
        to the correct value.
        """
        pass

    def recv_segment(self):
        """
        Blocks until a segment is avaiable to be read.
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
