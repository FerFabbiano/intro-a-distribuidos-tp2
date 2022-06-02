from threading import Thread
from application.file_utils import FileReader, FileWriter
from application.protocol import Opcode, ProtocolBuilder
from server.config import BATCH_FILE_SIZE
import logging
from transport_tcp.connection import Connection


class FSConnection:
    def __init__(self, connection: Connection, baseFsFolder):
        self.connection = connection
        self.baseFsFolder = baseFsFolder
        self.thread = Thread(target=self.run)
        self.thread.start()

    def run(self):
        logging.info("[ INFO NEW CONNECTION] - Running the new client")

        opcode = self.connection.recv(1)
        try:
            action = Opcode(opcode)

            print("[ INFO ] - Your clients wants to", str(action))

            if (action == Opcode.Upload):
                self.process_upload()
            elif (action == Opcode.Download):
                self.process_download()

        except ValueError:
            print("[ CONNECTION ]: Invalid OPCODE ", opcode)
        finally:
            self.connection.close()

    def process_upload(self):
        fs_length_raw = self.connection.recv_exact(4)
        file_size = ProtocolBuilder.file_size_parser(fs_length_raw)
        logging.debug('FILE SIZE: %i', file_size)

        fn_length_raw = self.connection.recv_exact(1)
        fn_length = ProtocolBuilder.fn_size_parser(fn_length_raw)
        logging.debug(' FN LENGTH: %i', fn_length)

        file_name_raw = self.connection.recv_exact(fn_length)
        file_name = ProtocolBuilder.fn_parser(file_name_raw)
        logging.debug('FN: %s', file_name)

        logging.info(
            "[ CONNECTION ] User wants to upload %s with size: %i", file_name, file_size)

        # Accept request
        res = ProtocolBuilder.accept_request()
        self.connection.send(res)

        path = f'{self.baseFsFolder}/{file_name}'

        with FileWriter(path, file_size) as file:
            while not file.end_of_file():
                print(f'[ CONNECTION ] waiting for data')
                buffer = self.connection.recv(BATCH_FILE_SIZE)
                print(f'[ CONNECTION ] recvd {len(buffer)} bytes')
                file.write_chunk(buffer)
        logging.debug('[ CONNECTION ] file written')

    def process_download(self):
        fn_length_raw = self.connection.recv(1)
        fn_length = ProtocolBuilder.fn_size_parser(fn_length_raw)

        file_name_raw = self.connection.recv(fn_length)
        file_name = ProtocolBuilder.fn_parser(file_name_raw)

        logging.info("[ CONNECTION ] User wants to download %s ", file_name)

        path = f'{self.baseFsFolder}/{file_name}'

        if not FileReader.file_exists(path):
            res = ProtocolBuilder.file_not_exists()
            self.connection.send(res)
            return

        file = FileReader(path)
        res = ProtocolBuilder.accept_download_request(file.file_size)
        self.connection.send(res)

        while not file.end_of_file():

            buffer = file.read_chunk(
                BATCH_FILE_SIZE
            )

            self.connection.send(buffer)

        file.close()

    def close(self):
        self.thread.join()
