import os
from threading import Thread
from application.file_utils import FileWriter
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

        try:
            opcode = self.connection.recv(1)
            action = Opcode(opcode)

            print("[ INFO ] - Your clients wants to", str(action))

            if (action == Opcode.Upload):
                self.process_upload()

        except ValueError:
            print("[ CONNECTION ]: Invalid OPCODE")
        finally:
            self.connection.close()
        # PROCESAR SI LA INFO ES CORRECTA
        # CASO UPLOAD
        # file_len = self.initial_payload[0:3]
        # file_name_len = self.initial_payload[4]
        # file_name = self.initial_payload[5:]

        # if file_len <= 0 or file_name_len <= 0:
        # INFORMAR EL ERROR AL CLIENTE Y CERRAR LA CONEXION

        # Y CONTESTARLE AL CLIENTE QUE ACEPTAMOS SU CONEXION

    def process_upload(self):

        fs_length_raw = self.connection.recv(4)
        file_size = ProtocolBuilder.file_size_parser(fs_length_raw)

        fn_length_raw = self.connection.recv(1)
        fn_length = ProtocolBuilder.fn_size_parser(fn_length_raw)

        file_name_raw = self.connection.recv(fn_length)
        file_name = ProtocolBuilder.fn_parser(file_name_raw)

        print('[ CONNECTION ] User wants to upload ',
              file_name, ' with size: ', file_size)

        # Accept request
        res = ProtocolBuilder.accept_request()
        self.connection.send(res)

        path = f'{BASE_FS_FOLDER}/{file_name}'

        file = FileWriter(path, file_size)
        while not file.end_of_file():
            buffer = self.connection.recv(BATCH_FILE_SIZE)
            file.write_chunk(buffer)

    def process_download(self):
        fn_length_raw = self.connection.recv(1)
        fn_length = ProtocolBuilder.fn_size_parser(fn_length_raw)

        file_name_raw = self.connection.recv(fn_length)
        file_name = ProtocolBuilder.fn_parser(file_name_raw)

        print('[ CONNECTION ] User wants to download ',
              file_name)

        path = f'{BASE_FS_FOLDER}/{file_name}'

        if not os.path.exists(path):
            res = ProtocolBuilder.file_not_exists()
            self.connection.send(res)
            return

        file_size = os.path.getsize(path)
        res = ProtocolBuilder.accept_upload_request(file_size)
        self.connection.send(res)

        file = FileWriter(path, file_size)

        while not file.end_of_file():
            buffer = self.connection.recv(BATCH_FILE_SIZE)
            file.write_chunk(buffer)

        file.close()

    def close(self):
        self.thread.join()
