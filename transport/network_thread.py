import select
import threading

from .segment import Segment

NETWORK_READ_INTERVAL = 0.25
BUFFER_SIZE = 65536

class NetworkThread:
    def __init__(self, socket, on_segment_received):
        self._thread = threading.Thread(target=self._thread_main)
        self._socket = socket
        self._on_segment_received = on_segment_received
        self._keep_alive = True
    
    def start(self):
        self._thread.start()

    def _thread_main(self):
        while self._keep_alive:
            rlist, _, _ = select.select([self._socket], [], [], NETWORK_READ_INTERVAL)
            if not rlist:
                continue
            data, remote_address = self._socket.recvfrom(BUFFER_SIZE)
            segment = Segment.from_datagram(data)
            if not segment.is_checksum_correct():
                print(f'[NetworkThread@{remote_address}]: Invalid checksum {repr(segment)}')
                continue
            print(f'<R {repr(segment)}')
            self._on_segment_received(segment, remote_address)
        
    def stop(self):
        self._keep_alive = False
        self._thread.join()