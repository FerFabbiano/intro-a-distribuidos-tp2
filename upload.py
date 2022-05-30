from threading import Thread
from application.file_utils import FileReader
from client.client_upload import ClientUploadConnection
from client.client_utils import build_upload_parser, finish_or_wait_quit
from transport_tcp.connection import Connection

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65433  # The port used by the server
BUFFER_SIZE = 508


def main():
    args = build_upload_parser().parse_args()

    server_port = int(args.port)
    source_file_path = args.src
    file_name_dst = args.name

    if not FileReader.file_exists(source_file_path):
        print(
            "[ ERROR ] - "
            "File {} not found. Please provide a correct file path "
            .format(source_file_path)
        )
        return

    print("[ INFO ] - Got server port: {}".format(server_port))
    print("[ INFO ] - Got source file path: {}".format(source_file_path))
    print("[ INFO ] - Got file name: {}".format(file_name_dst))

    connection = Connection.connect(HOST, server_port)
    print("[ INFO ] - Nueva conexión generada con el servidor")

    client = ClientUploadConnection(
        connection,
        file_name_dst,
        source_file_path
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
