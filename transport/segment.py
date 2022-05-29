# Opcodes: 
#   - NewConnection = 0x10; No payload 
#   - Data = 0x21; Payload = data
#   - Ack = 0x32; For Stop & Wait: no payload, for Selective Repeat: payload = ACK data
#   - Close = 0x43; No payload
#
# Checksum: opcode XOR payload_size.low XOR ~(payload_size.high)
#
#    0 ------ 8 ------ 16 ------ 24 ------ 32 
#  0 | opcode |   payload size   | checksum |
#  4 |           sequence number            | 
#
import time

from enum import enum


class Opcode(Enum):
    NewConnection = 0x10
    Data = 0x21
    AckStopAndWait = 0x32
    AckSelectiveRepeat = 0x33
    Close = 0x43


class Segment:
    def __init__(self, opcode, payload, sequence_number, checksum=None, payload_size=None):
        self.opcode = opcode
        self.payload = payload
        self.sequence_number = sequence_number
        self.creation_time = time.now()

        self.checksum = checksum
        self.payload_size_correct = len(self.payload) == payload_size
    
    @staticmethod
    def from_datagram(self, raw_data: bytes):
        opcode, payload_size, checksum, sequence_number = struct.unpack("!BHBI", raw_data[:4])
        return Segment(opcode, raw_data[4:], sequence_number, checksum=checksum, payload_size=payload_size)
    
    def is_checksum_correct(self):
        assert checksum is not None, 'No checksum to check'
        return self.checksum == self.calculate_checksum()
    
    def calculate_checksum(self):
        payload_low = len(self.payload) & 0xFF
        payload_high = (len(self.payload) >> 8) & 0xFF
        return self.opcode ^ payload_low ^ (~payload_high)
    
    def serialize(self) -> bytes:
        header = struct.pack("!BHBI", 
                             self.opcode, 
                             len(self.payload), 
                             self.calculate_checksum(), 
                             self.sequence_number)
        segment = header + payload
        assert len(segment) <= MAX_UDP_DATAGRAM_SIZE, \
            f"Segment won't fit in a datagram ({len(segment)} >= {MAX_UDP_DATAGRAM_SIZE})"
        return segment
