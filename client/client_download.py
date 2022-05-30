from time import sleep
from application.protocol import Opcode, ProtocolBuilder

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
                self.download_process()

        except ValueError:
            print("[ ERROR ]: Invalid OPCODE")

    def download_process(self):
        print("[ INFO ] - Downloading file from server")

        while self.keep_alive:
            sleep(20)

    def close(self):
        self.keep_alive = False
