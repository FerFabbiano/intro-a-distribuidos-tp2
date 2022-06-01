from threading import Thread
from application.file_utils import FileReader, FileWriter
from application.protocol import Opcode, ProtocolBuilder
from server.config import BASE_FS_FOLDER, BATCH_FILE_SIZE

from transport_tcp.connection import Connection


class FSConnection:
    def __init__(self, connection: Connection):
        self.connection = connection

        self.thread = Thread(target=self.run)
        self.thread.start()

    def run(self):
        print("[ INFO NEW CONNECTION] - Running the new client")

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
        print('FILE SIZE:', file_size)

        fn_length_raw = self.connection.recv_exact(1)
        fn_length = ProtocolBuilder.fn_size_parser(fn_length_raw)
        print('FN LENGTH:', fn_length)

        file_name_raw = self.connection.recv_exact(fn_length)
        file_name = ProtocolBuilder.fn_parser(file_name_raw)
        print('FN:', file_name)

        print('[ CONNECTION ] User wants to upload ',
              file_name, ' with size: ', file_size)

        # Accept request
        res = ProtocolBuilder.accept_request()
        self.connection.send(res)

        path = f'{BASE_FS_FOLDER}/{file_name}'

        with FileWriter(path, file_size) as file:
            while not file.end_of_file():
                print('[ CONNECTION ] waiting for data')
                buffer = self.connection.recv(BATCH_FILE_SIZE)
                print(f'[ CONNECTION ] recvd {len(buffer)} bytes')
                file.write_chunk(buffer)
        print('[ CONNECTION ] file written')

    def process_download(self):
        fn_length_raw = self.connection.recv(1)
        fn_length = ProtocolBuilder.fn_size_parser(fn_length_raw)

        file_name_raw = self.connection.recv(fn_length)
        file_name = ProtocolBuilder.fn_parser(file_name_raw)

        print('[ CONNECTION ] User wants to download ', file_name)

        path = f'{BASE_FS_FOLDER}/{file_name}'

        if not FileReader.file_exists(path):
            res = ProtocolBuilder.file_not_exists()
            self.connection.send(res)
            return

        file = FileReader(path)
        res = ProtocolBuilder.accept_download_request(file.file_size)
        self.connection.send(res)

        print('REQUEST ACEPTADO')
        while not file.end_of_file():

            buffer = file.read_chunk(
                BATCH_FILE_SIZE
            )

            self.connection.send(buffer)

        file.close()

    def close(self):
        self.thread.join()
