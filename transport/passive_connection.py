import time

from .rdp import RdpController, StopAndWaitRdpController
from .raw_connection import RawConnection
from .connection import Connection
from .segment import Segment
import threading

class PassiveConnection(Connection):
    def __init__(self, address, controller: RdpController, welcome_segment: Segment):
        self._controller = controller
        self._recv_buffer = bytes()
        super().__init__(address, self._controller)

        self._controller.do_passive_handshake(welcome_segment)

    def close(self):
        self._controller.close()
