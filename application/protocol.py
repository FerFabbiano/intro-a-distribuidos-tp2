
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


class Opcode(Enum):
    Upload = 0x10
    Download = 0x11
