# Opcodes:
#   - StartDownload = 0x10;
#   - StartUpload = 0x11;
#
# UPLOAD
#   opcode: 1 byte.
#   filesize: 4 bytes.
#   filename size: 1 byte.
#   file name: <dynamic>.
#
# DOWNLOAD
#   opcode: 1 byte.
#   filename size: 1 byte.
#   file name: <dynamic>.

from enum import Enum
import struct

BASE_FS_FOLDER = 'files'
BATCH_FILE_SIZE = 500


class Opcode(Enum):
    Upload = b"0"
    Download = b"1"
    Accepted = b"2"


class ProtocolBuilder:
    @staticmethod
    def accept_request():
        return Opcode.Accepted.value

    "bytes is a size 4 unsigned integer"

    @staticmethod
    def file_size_parser(bytes) -> int:
        return struct.unpack("!I", bytes)[0]

    @staticmethod
    def fn_size_parser(byte) -> int:
        return struct.unpack("b", byte)[0]

    @staticmethod
    def fn_parser(bytes) -> str:
        return bytes.decode('ascii')

    @staticmethod
    def upload_request(file_name: str, file_size: int):
        opcode = Opcode.Upload.value
        file_size_bytes = struct.pack("!I", file_size)
        file_name_size_bytes = struct.pack("b", len(file_name))

        return (
            opcode +
            file_size_bytes +
            file_name_size_bytes +
            bytes(file_name, "ascii")
        )

    @staticmethod
    def download_request(file_name: str):
        opcode = Opcode.Download.value
        file_name_size_bytes = struct.pack("b", len(file_name))

        return (
            opcode +
            file_name_size_bytes +
            bytes(file_name, "ascii")
        )
