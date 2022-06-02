import time
import socket
import select

from threading import Thread, Timer
from queue import Queue

from .rdt_controller import DefaultRdtController
from .segment import Segment, Opcode
from .rdp import StopAndWaitRdpController
from .raw_connection import RawConnection
from .network_thread import NetworkThread
from .connection import NETWORK_TICK_SECONDS
from .passive_connection import PassiveConnection
import logging


class Listener:
    def __init__(self, host, port, ControllerType=None):
        self.src_address = (host, port)
        self.socket = None
        self.keep_running = True
        self.new_connections = Queue()
        self.connections = {}
        self._network_thread = None
        self._timer = Timer(NETWORK_TICK_SECONDS, self.on_tick)
        # self._ControllerType = ControllerType or StopAndWaitRdpController
        self._ControllerType = ControllerType or DefaultRdtController
        self._closing = False

        self.start()

    def start(self):
        if self.socket or self._network_thread:
            raise Exception("The server is already running!")

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(self.src_address)
        self._timer = Timer(NETWORK_TICK_SECONDS, self.on_tick)
        self._network_thread = NetworkThread(
            self.socket, self.on_segment_received)
        self._timer.start()
        self._network_thread.start()

    def on_tick(self):
        # Push timer events and do some clean up
        connections_to_remove = []
        for address, connection in self.connections.items():
            if not connection.is_alive():
                connections_to_remove.append(address)
            else:
                connection.on_tick()

        # Remove old connections
        for address in connections_to_remove:
            self.connections.pop(address)

        if not self._closing:
            self._timer = Timer(NETWORK_TICK_SECONDS, self.on_tick).start()

    def on_segment_received(self, segment, remote_address):
        if remote_address in self.connections:
            self.connections[remote_address].on_segment_received(
                segment, remote_address)
        elif segment.opcode == Opcode.NewConnection:
            logging.info(
                "[Listener] New connection from: {} ".format(remote_address))
            self.connections[remote_address] = PassiveConnection(
                remote_address,
                self._ControllerType(RawConnection(
                    self.socket, remote_address)),
                segment
            )
            self.new_connections.put(self.connections[remote_address])
        else:
            logging.info(
                f"[Listener@{remote_address}] Segment received for unknown connection")

    def get_new_connection(self):
        return self.new_connections.get()

    def close(self):
        if (
                not self.socket
                or not self._network_thread
        ):
            raise Exception("The server is not running!")

        self._closing = True

        self.keep_running = False
        self.new_connections.put(None)
        self._network_thread.stop()
