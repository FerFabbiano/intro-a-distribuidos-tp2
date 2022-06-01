import socket

from .rdp import StopAndWaitRdpController
from .raw_connection import RawConnection
from .connection import Connection, NETWORK_TICK_SECONDS
from .network_thread import NetworkThread
import threading


class ActiveConnection(Connection):
    def __init__(self, host, port, ControllerType=None):
        if ControllerType is None:
            ControllerType = StopAndWaitRdpController

        self._recv_buffer = bytes()
        self._timer = threading.Timer(NETWORK_TICK_SECONDS, self.on_tick)
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._network_thread = NetworkThread(
            self._socket, self.on_segment_received)
        self._controller = ControllerType(
            RawConnection(self._socket, (host, port)))
        self._closing = False
        self._timer.start()
        self._network_thread.start()
        super().__init__((host, port), self._controller)
        self._controller.do_active_handshake()

    def on_tick(self):
        super().on_tick()
        if not self._closing:
            self._timer = threading.Timer(
                NETWORK_TICK_SECONDS, self.on_tick).start()

    def close(self):
        self._closing = True
        self._network_thread.stop()
        self._socket.close()
