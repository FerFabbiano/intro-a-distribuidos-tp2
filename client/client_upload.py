from application.file_utils import FileReader
from application.protocol import Opcode, ProtocolBuilder

from transport_tcp.connection import Connection

CHUNK_SIZE = 500


class ClientUploadConnection:
    def __init__(
        self,
        connection: Connection,
        file_name: str,
        file_size: int,
        source_file_path: str,
    ):
        self.connection = connection
        self.keep_alive = True
        self.handshake = False
        self.file_name = file_name
        self.file = FileReader(source_file_path, file_size)

    def run(self):

        # Handshake to upload
        handshake_msg_bytes = ProtocolBuilder.upload_request(
            self.file_name, self.file.file_size
        )

        print(
            "[ INFO ] - Upload handshake msg: {}"
            .format(handshake_msg_bytes)
        )
        self.connection.send(handshake_msg_bytes)

        # Receive firts byte of opcode
        data = self.connection.recv(1)
        try:
            action = Opcode(data).value

            if action == Opcode.Accepted.value:
                print(
                    "[ SUCCESS ] - "
                    "Connection accepted by server to upload file."
                )
                self.upload_process()

        except ValueError:
            print("[ ERROR ]: Invalid OPCODE")

    def upload_process(self):

        while self.keep_alive and not self.file.end_of_file():

            file_bytes = self.file.read_chunk(
                CHUNK_SIZE
            )

            print(
                "[ INFO ] - Read {} bytes from file. Sending to server."
                .format(str(len(file_bytes)))
            )

            self.connection.send(file_bytes)
            print(
                "[ SUCCESS ] - Sent {} bytes to server."
                .format(str(len(file_bytes)))
            )

    def close(self):
        self.keep_alive = False
        self.file.close()
