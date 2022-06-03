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
# C> SEGMENTO(opcode=NewConnection, seq=1, payload_sz=0)
# <S SEGMENTO(opcode=NewConnection, seq=1, payload_sz=0)
# C> SEGMENTO(opcode=Ack, seq=1)
# ** connection is established **
# L> SEGMENTO(opcode=Data, payload_sz=4, seq=1, payload="HOLA") 
# <R SEGMENTO(opcode=Ack, seq=1, payload_sz=0)
# <R SEGMENTO(opcode=Data, payload_sz=4, payload="CHAU", seq=1)
# *loss* L> SEGMENTO(opcode=Ack, seq=1, payload_sz=0)
# <R SEGMENTO(opcode=Data, payload_sz=4, payload="CHAU", seq=1)
# L> SEGMENTO(opcode=Ack, seq=1, payload_sz=0)
#
# C> Segment(opcode=Close, seqnum)  # state = _closing
# <S Segment(opcode=Close, seqnum)
# <S Segment(opcode=Ack)            
# ** time wait 2*rto **


import struct
import time

from enum import Enum

HEADER_SIZE = 8
MAX_PAYLOAD_SIZE = 500
MAX_UDP_DATAGRAM_SIZE = HEADER_SIZE + MAX_PAYLOAD_SIZE

class Opcode(Enum):
    NewConnection = 0x10
    Data = 0x21
    Ack = 0x32
    Close = 0x43


class Segment:
    def __init__(self, opcode, payload=None, checksum=None, payload_size=None):
        if payload is None:
            payload = bytes()
        self.opcode = opcode
        self.payload = payload
        self.sequence_number = 0
        self.creation_time = time.time()
        self.retries = 0

        self.checksum = checksum
        self.payload_size_correct = len(self.payload) == payload_size
    
    @staticmethod
    def from_datagram(raw_data: bytes):
        header, payload = raw_data[:8], raw_data[8:]
        opcode, payload_size, checksum, sequence_number = struct.unpack("!BHBI", header)
        segment = Segment(Opcode(opcode), payload, checksum=checksum, payload_size=payload_size)
        segment.sequence_number = sequence_number
        return segment
    
    def is_checksum_correct(self):
        assert self.checksum is not None, 'No checksum to check'
        return self.checksum == self.calculate_checksum()
    
    def calculate_checksum(self):
        payload_low = len(self.payload) & 0xFF
        payload_high = (len(self.payload) >> 8) & 0xFF
        return (self.opcode.value ^ payload_low ^ (~payload_high)) & 0xFF
    
    def serialize(self) -> bytes:
        header = struct.pack("!BHBI", 
                             self.opcode.value, 
                             len(self.payload), 
                             self.calculate_checksum(), 
                             self.sequence_number)
        segment = header + self.payload
        assert len(segment) <= MAX_UDP_DATAGRAM_SIZE, \
            f"Segment won't fit in a datagram ({len(segment)} >= {MAX_UDP_DATAGRAM_SIZE})"
        return segment

    def __repr__(self):
        payload_repr = repr(self.payload[:10])
        if len(self.payload) > 10:
            payload_repr += '...'

        return f'Segment({Opcode(self.opcode)}, seq={self.sequence_number}, {payload_repr})'
    
    def __str__(self):
        return repr(self)