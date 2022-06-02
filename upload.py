from threading import Thread
from application.file_utils import FileReader
from client.client_upload import ClientUploadConnection
from client.client_utils import build_upload_parser, finish_or_wait_quit
from transport.connection import Connection
import logging

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65433  # The port used by the server
BUFFER_SIZE = 508


def main():
    args = build_upload_parser().parse_args()

    logging.basicConfig(
        format='%(asctime)s - %(message)s', datefmt='%H:%M:%S',
        level=args.loglevel)

    server_port = int(args.port)
    source_file_path = args.src
    file_name_dst = args.name

    if not FileReader.file_exists(source_file_path):
        logging.error(
            "[ ERROR ] - "
            "File {} not found. Please provide a correct file path "
            .format(source_file_path)
        )
        return

    logging.debug("[ INFO ] - Got server port: {}".format(server_port))
    logging.debug(
        "[ INFO ] - Got source file path: {}".format(source_file_path))
    logging.debug("[ INFO ] - Got file name: {}".format(file_name_dst))

    connection = Connection.connect(HOST, server_port)
    logging.debug("[ INFO ] - Nueva conexión generada con el servidor")

    client = ClientUploadConnection(
        connection,
        file_name_dst,
        source_file_path
    )

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
