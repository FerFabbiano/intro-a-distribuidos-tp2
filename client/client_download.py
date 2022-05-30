from application.file_utils import FileWriter
from application.protocol import Opcode, ProtocolBuilder
from server.config import BATCH_FILE_SIZE
from transport_tcp.connection import Connection
import os


class ClientDownloadConnection:
    def __init__(
        self,
        connection: Connection,
        file_name: str,
        file_size: int,
        destination_file_path: str,
    ):
        self.connection = connection
        self.keep_alive = True
        self.file_name = file_name
        self.file_size = file_size
        self.destination_file_path = destination_file_path

    def run(self):
        # Handshake to download
        handshake_msg_bytes = ProtocolBuilder.download_request(
            self.file_name
        )

        print(
            "[ INFO ] - Download handshake msg: {}"
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
                    "Connection accepted by server to download file."
                )

                # Get file size
                fs_length_raw = self.connection.recv(4)
                file_size = ProtocolBuilder.file_size_parser(fs_length_raw)
                self.file_size = file_size

                self.download_process()
            elif action == Opcode.FileNotFound.value:
                print(
                    "[ WARN ] - "
                    "File {} not found in server".format(self.file_name)
                )

        except ValueError:
            print("[ ERROR ]: Invalid OPCODE")

    def download_process(self):
        print("[ INFO ] - Downloading file from server")

        if not os.path.dirname(self.destination_file_path):
            print(
                    "[ WARN ] - "
                    "Directory {} not found. Pleasea create directory "
                    "or select another"
                    .format(self.file_name)
                )
            return

        file = FileWriter(self.destination_file_path, self.file_size)
        while not file.end_of_file():
            buffer = self.connection.recv(BATCH_FILE_SIZE)
            file.write_chunk(buffer)

    def close(self):
        self.keep_alive = False
