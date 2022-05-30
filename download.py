from threading import Thread
from client.client_download import ClientDownloadConnection
from client.client_utils import build_download_parser, finish_or_wait_quit
from transport_tcp.connection import Connection
import os

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65433  # The port used by the server
BUFFER_SIZE = 508


def main():
    args = build_download_parser().parse_args()

    server_port = int(args.port)
    destination_file_path = args.dst
    file_name_dst = args.name

    # TODO: REVISAR ESTO
    if not os.path.dirname(destination_file_path):
        print(
            "[ WARN ] - "
            "Directory {} not found. Pleasea create directory "
            "or select another"
            .format(destination_file_path)
        )
        return

    print("[ INFO ] - Got server port: {}".format(server_port))
    print(
        "[ INFO ] - Got destination file path: {}"
        .format(destination_file_path)
    )
    print("[ INFO ] - Got file name: {}".format(file_name_dst))

    connection = Connection.connect(HOST, server_port)
    print("[ INFO ] - Nueva conexión generada con el servidor")

    client = ClientDownloadConnection(
        connection,
        file_name_dst,
        destination_file_path
    )

    thread = Thread(target=client.run)
    thread.start()

    finish_or_wait_quit(client)

    print(
        "[ INFO ] - Comienzo cierre de conexión con servidor."
        "Joineando threads."
    )

    client.close()
    thread.join()
    print("[ INFO ] - Thread joineados exitosamente! Terminando programa.")

    return 0


main()
