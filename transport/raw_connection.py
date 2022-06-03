import socket
import logging
from .segment import Opcode
from threading import Timer
import random

FAKE_RTT_ENABLED = True
FAKE_RTT_SECONDS = 0.40

PACKET_LOSS_ENABLED = True
PACKET_LOSS_RATE = 0.10

class RawConnection:
    def __init__(self, socket, destination_address):
        self.socket = socket
        self.destination_address = destination_address

    def send_segment(self, segment):
        if FAKE_RTT_ENABLED:
            Timer(FAKE_RTT_SECONDS, lambda: self._do_send_segment(segment)).start()
        else:
            self._do_send_segment(segment)

    def _do_send_segment(self, segment):
        if PACKET_LOSS_ENABLED:
            if random.random() < PACKET_LOSS_RATE:
                print(f'DROPPED: {repr(segment)}')
                return
        logging.debug(f'L> {repr(segment)}')
        self.socket.sendto(segment.serialize(), self.destination_address)