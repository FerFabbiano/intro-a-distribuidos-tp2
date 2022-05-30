from application.protocol import Opcode, ProtocolBuilder
from client.client_utils import read_file_chunk

from transport_tcp.connection import Connection


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
        self.file_size = file_size
        self.source_file_path = source_file_path

    def run(self):
        # Handshake to upload
        handshake_msg_bytes = ProtocolBuilder.upload_request(
            self.file_name, self.file_size
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
        file_read_offset = 0
        print(
            "[ INFO ] - Reading file from path: {}"
            .format(self.source_file_path)
        )

        while self.keep_alive and (file_read_offset < self.file_size):

            file_bytes = read_file_chunk(
                self.source_file_path,
                file_read_offset
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

            file_read_offset += len(file_bytes)
            print(
                "Total bytes read from file: {}"
                .format(str(file_read_offset))
            )

    def close(self):
        self.keep_alive = False
