import time

from threading import Thread
from .segment import Segment, Opcode


class Listener:
    def __init__(self, host, port):
        self.src_address = (host, port)
        self.socket = None
        self.keep_running = True
        self.new_connections = Queue()
        self.connections = {}
        self.network_thread = None
        self.timers_thread = None

    def start(self):
        if self.socket or self.network_thread or self.timers_thread:
            raise Exception("The server is already running!")

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(self.src_address)
        self.timers_thread = Thread(target=self._run_timers)
        self.network_thread = Thread(target=self._run_network)
        self.timers_thread.start()
        self.network_thread.start()

    def _run_network(self):
        while self.keep_running:
            try:
                msg, client_address = self.socket.recvfrom(BUFFER_SIZE)
                segment = Segment.from_datagram(msg)
                if not segment.is_checksum_correct():
                    print(
                        "[Listener.run_network] Segment with invalid checksum: ", segment)
                    continue

                if segment.opcode == Opcode.NewConnection:
                    print("[ INFO IN NEW CONNECTION ] - ", msg[1:])
                    self.connections[client_address] = Connection(self)
                    self.new_connections.put(self.connections[client_address])
                else:
                    connection = self.connections.get(client_address)
                    # if segment.opcode == Opcode.
            except Exception as e:
                print("[Listener.run_network] Exception occured: ", e)

    def _run_timers(self):
        while self.keep_running:
            time.sleep(0.010)

            # Push timer events and do some clean up
            connections_to_remove = []
            for address, connection in self.connections.items():
                if not connection.is_alive():
                    connections_to_remove.append(address)
                else:
                    connection.on_event(TimerEvent(time.now()))

            # Remove old connections
            for address in connections_to_remove:
                self.connections.pop(address)

    def stop(self):
        if not self.socket or not self.network_thread or not self.timers_thread:
            raise Exception("The server is not running!")

        self.keep_running = False
        self.new_connections.put(None)
        self.socket.close()
        self.timers_thread.join()
        self.network_thread.join()
