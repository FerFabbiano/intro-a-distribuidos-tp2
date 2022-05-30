from application.protocol import Opcode, ProtocolBuilder
import os
from server.config import BATCH_FILE_SIZE
from transport_tcp.connection import Connection


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
        self.handshake = False
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

        if not os.path.exists(self.destination_file_path):
            os.makedirs(self.destination_file_path)

        bytes_downloaded = 0
        while self.keep_alive and (bytes_downloaded < self.file_size):
            with open(
                    f'{self.destination_file_path}/{self.file_name}',
                    'wb+'
                    ) as f:

                # Replace any existing file
                f.seek(0)
                f.truncate()

                while(bytes_downloaded < self.file_size):

                    buffer = self.connection.recv(BATCH_FILE_SIZE)

                    bytes_downloaded += len(buffer)

                    f.write(buffer)

    def close(self):
        self.keep_alive = False
