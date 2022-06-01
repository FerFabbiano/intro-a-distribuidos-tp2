from application.file_utils import FileReader
from application.protocol import Opcode, ProtocolBuilder

from transport.connection import Connection

CHUNK_SIZE = 500


class ClientUploadConnection:
    def __init__(
        self,
        connection: Connection,
        file_name: str,
        source_file_path: str,
    ):
        self.connection = connection
        self.keep_alive = True
        self.file_name = file_name
        self.source_file_path = source_file_path

    def run(self):

        self.send_upload_request()

        # Receive firts byte of opcode
        try:
            data = self.connection.recv(1)
            action = Opcode(data)

            if action == Opcode.Accepted:
                self.upload_process()

        except ValueError:
            print("[ ERROR ]: Invalid OPCODE")

        self.keep_alive = False

    def send_upload_request(self):
        # Handshake to upload
        file_size = FileReader.file_size(self.source_file_path)
        handshake_msg_bytes = ProtocolBuilder.upload_request(
            self.file_name,
            file_size
        )

        print(
            "[ INFO ] - Upload handshake msg: {}"
            .format(handshake_msg_bytes)
        )
        self.connection.send(handshake_msg_bytes)

    def upload_process(self):

        print(
            "[ SUCCESS ] - "
            "Connection accepted by server to upload file."
        )

        with FileReader(self.source_file_path) as file:
            while self.keep_alive and not file.end_of_file():

                file_bytes = file.read_chunk(
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
            print(f'[Quitting upload loop] {self.keep_alive=} {file.end_of_file()=}')

    def close(self):
        self.keep_alive = False
