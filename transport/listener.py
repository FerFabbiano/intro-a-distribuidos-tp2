import time
import socket
import select

from threading import Thread
from queue import Queue
from .segment import Segment, Opcode
from .rdp import StopAndWaitRdpController
from .raw_connection import RawConnection
from .connection import Connection

BUFFER_SIZE = 65536

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
                ready = select.select([self.socket], [], [], 0.5)
                if not ready[0]:
                    continue
                
                msg, client_address = self.socket.recvfrom(BUFFER_SIZE)
                segment = Segment.from_datagram(msg)
                if not segment.is_checksum_correct():
                    print("[Listener.run_network] Segment with invalid checksum: ", segment)
                    continue
                print(segment)

                if segment.opcode == Opcode.NewConnection:
                    print("[Listener.run_network] New connection from: ", client_address)
                    controller = StopAndWaitRdpController(RawConnection(self.socket, client_address))
                    assert controller.try_send_segment(Segment(Opcode.NewConnectionReply, bytes()))
                    self.connections[client_address] = Connection(controller)
                    self.new_connections.put(self.connections[client_address])
                else:
                    connection = self.connections.get(client_address)
                    if not connection:
                        print("[Listener.run_network] Segment for no known connection: ", segment, client_address)
                        continue
                    
                    if segment.opcode == Opcode.NewConnectionReply:
                        connection.on_new_connection_reply(segment)
                    elif segment.opcode == Opcode.Data:
                        connection.on_data_received(segment)
                    elif segment.opcode == Opcode.Ack:
                        connection.on_ack_received(segment)
                    elif segment.opcode == Opcode.Close:
                        connection.on_close(segment)
                    else:
                        print("[Listener.run_network] Unknown opcode: ", segment)
            except ValueError as e:
                print("[Listener.run_network] Exception occured: ", e)
        self.socket.close()
    
    def _run_timers(self):
        while self.keep_running:
            time.sleep(0.010)

            # Push timer events and do some clean up
            connections_to_remove = []
            for address, connection in self.connections.items():
                if not connection.is_alive():
                    connections_to_remove.append(address)
                else:
                    connection.on_tick(time.time())

            # Remove old connections
            for address in connections_to_remove:
                self.connections.pop(address)
    
    def get_new_connection(self):
        return self.new_connections.get()

    def stop(self):
        if not self.socket or not self.network_thread or not self.timers_thread:
            raise Exception("The server is not running!")

        self.keep_running = False
        print("after self.keep_running = False")
        self.new_connections.put(None)
        print("after self.new_connections.put(None)")
        self.timers_thread.join()
        print("after self.timers_thread.join()")
        self.network_thread.join()
        print("after self.network_thread.join()")
        
