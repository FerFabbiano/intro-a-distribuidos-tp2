from application.file_utils import FileWriter
from application.protocol import Opcode, ProtocolBuilder
from server.config import BATCH_FILE_SIZE
from transport.connection import Connection
import logging


class ClientDownloadConnection:
    def __init__(
        self,
        connection: Connection,
        file_name: str,
        destination_file_path: str,
    ):
        self.connection = connection
        self.keep_alive = True
        self.file_name = file_name
        self.destination_file_path = destination_file_path

    def run(self):

        self.send_download_request()

        try:
            # Receive firts byte of opcode
            data = self.connection.recv(1)
            action = Opcode(data)

            if action == Opcode.Accepted:
                self.download_process()

            elif action == Opcode.FileNotFound:
                logging.warning("[ WARN ] - "
                                "File {} not found in server".format(self.file_name))

            self.connection.close()
        except ValueError:
            logging.error("[ ERROR ]: Invalid OPCODE")

    def send_download_request(self):
        # Handshake to download
        handshake_msg_bytes = ProtocolBuilder.download_request(
            self.file_name
        )

        logging.debug("[ DEBUG] - Download handshake msg: {}"
                      .format(handshake_msg_bytes))

        self.connection.send(handshake_msg_bytes)

    def download_process(self):

        logging.info("[ SUCCESS ] - "
                     "Connection accepted by server to download file.")

        # Get file size
        fs_length_raw = self.connection.recv(4)
        file_size = ProtocolBuilder.file_size_parser(fs_length_raw)

        with FileWriter(self.destination_file_path, file_size) as file:
            while self.keep_alive and not file.end_of_file():
                buffer = self.connection.recv(BATCH_FILE_SIZE)
                file.write_chunk(buffer)

    def close(self):
        self.keep_alive = False
