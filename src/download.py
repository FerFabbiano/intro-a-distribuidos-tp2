from client.client_download import ClientDownloadConnection
from client.client_utils import build_download_parser
from transport.connection import Connection
import os
import logging

BUFFER_SIZE = 508


def main():
    args = build_download_parser().parse_args()

    logging.basicConfig(
        format='%(asctime)s - %(message)s', datefmt='%H:%M:%S',
        level=args.loglevel)

    server_port = int(args.port)
    destination_file_path = args.dst
    file_name_dst = args.name

    logging.info("[INFO] Cliente iniciado, se realizara un download")

    # TODO: REVISAR ESTO
    if not os.path.dirname(destination_file_path):
        logging.warning(
            "[ WARN ] - "
            "Directory {} not found. Pleasea create directory "
            "or select another"
            .format(destination_file_path)
        )
        return

    logging.debug("[ INFO ] - Got server port: {}".format(server_port))
    logging.debug(
        "[ INFO ] - Got destination file path: {}"
        .format(destination_file_path)
    )
    logging.debug("[ INFO ] - Got file name: {}".format(file_name_dst))

    logging.info(
        "[INFO] Se establecera una conexion con el host : {} y port: {}"
        .format(args.host, server_port))

    connection = Connection.connect(args.host, server_port)

    client = ClientDownloadConnection(
        connection,
        file_name_dst,
        destination_file_path
    )

    # finish_or_wait_quit(client)

    client.run()
    client.close()

    logging.debug(
        "[ INFO ] - Thread joineados exitosamente! Terminando programa.")
    logging.info("[INFO] El cliente se ha cerrado exitosamente")

    return 0


main()
