from .rdt import RdtController
from .connection import Connection
from .segment import Segment


class PassiveConnection(Connection):
    def __init__(self, address, controller: RdtController,
                 welcome_segment: Segment):
        self._controller = controller
        self._recv_buffer = bytes()
        super().__init__(address, self._controller)

        self._controller.do_passive_handshake(welcome_segment)
