from threading import Thread

from transport_tcp.connection import Connection


class FSConnection:
    def __init__(self, connection: Connection):
        self.connection = connection

        self.thread = Thread(target=self.run)
        self.thread.start()

    def run(self):
        print("[ INFO NEW CONNECTION] - Running the new client")

        opcode = self.connection.recv(1)

        print("[ INFO ] - Your clients wants to")

        # PROCESAR SI LA INFO ES CORRECTA
        # CASO UPLOAD
        # file_len = self.initial_payload[0:3]
        # file_name_len = self.initial_payload[4]
        # file_name = self.initial_payload[5:]

        # if file_len <= 0 or file_name_len <= 0:
        # INFORMAR EL ERROR AL CLIENTE Y CERRAR LA CONEXION

        # Y CONTESTARLE AL CLIENTE QUE ACEPTAMOS SU CONEXION

    def close(self):
        self.thread.join()
