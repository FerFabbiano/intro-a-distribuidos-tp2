import sys
import select
from threading import Thread
from client.client_download import ClientDownloadConnection
from client.client_utils import build_download_parser, finish_or_wait_quit
from transport.connection import Connection
import os
import logging

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65434  # The port used by the server
BUFFER_SIZE = 508


def main():
    args = build_download_parser().parse_args()

    logging.basicConfig(
        format='%(asctime)s - %(message)s', datefmt='%H:%M:%S',
        level=args.loglevel)

    server_port = int(args.port)
    destination_file_path = args.dst
    file_name_dst = args.name

    # TODO: REVISAR ESTO
    if not os.path.dirname(destination_file_path):
        logging.warning(
            "[ WARN ] - "
            "Directory {} not found. Pleasea create directory "
            "or select another"
            .format(destination_file_path)
        )
        return

    logging.info("[ INFO ] - Got server port: {}".format(server_port))
    logging.debug(
        "[ INFO ] - Got destination file path: {}"
        .format(destination_file_path)
    )
    logging.debug("[ INFO ] - Got file name: {}".format(file_name_dst))

    connection = Connection.connect(HOST, server_port)
    logging.debug("[ INFO ] - Nueva conexión generada con el servidor")

    client = ClientDownloadConnection(
        connection,
        file_name_dst,
        destination_file_path
    )

    # finish_or_wait_quit(client)

    logging.debug(
        "[ INFO ] - Comienzo cierre de conexión con servidor."
        "Joineando threads."
    )

    client.run()
    client.close()

    logging.debug(
        "[ INFO ] - Thread joineados exitosamente! Terminando programa.")

    return 0


main()

# def main():
#     # while(True):
#     # s.sendto(b"NCLIENTE NUEVO", (HOST, PORT))
#     connection = Connection.connect(HOST, PORT)
#     print("[ NUEVA CONEXION ]")
#     sleep(100000)
#     print(str(connection))
#     # (recvData, serverAddress) = s.recvfrom(BUFFER_SIZE)

#     # Poner validacion de que solo el servidor me mande mensajes

#     # s.sendto(b"C", (HOST, PORT))
#     # (recvData, serverAddress) = s.recvfrom(BUFFER_SIZE)

#     # print("[ PROTOCOL ACK ] - ", str(recvData))


# main()
# print(f"Received {data!r}")
