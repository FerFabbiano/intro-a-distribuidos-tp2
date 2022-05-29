import argparse


HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65432  # The port used by the server
CHUNK_SIZE = 500


def build_parser():
    my_parser = argparse.ArgumentParser()

    group = my_parser.add_mutually_exclusive_group()
    group.add_argument(
        "-v", "--verbose", help="increase output verbosity", action="store_true"
    )
    group.add_argument(
        "-q", "--quiet", help="decrease output verbosity", action="store_true"
    )
    my_parser.add_argument("-H", "--host", help="server IP address", metavar="")
    my_parser.add_argument(
        "-p", "--port", help="server port", required=True, metavar=""
    )
    my_parser.add_argument(
        "-s", "--src", help="source file path", required=True, metavar=""
    )
    my_parser.add_argument("-n", "--name", help="file name", required=True, metavar="")

    return my_parser


def read_file(path):
    file = open(path, "rb")

    chunk = file.read(CHUNK_SIZE)

    while chunk:
        print(chunk)
        chunk = file.read(CHUNK_SIZE)

    return 0


def main():
    args = build_parser().parse_args()

    server_port = args.port
    source_file_path = args.src
    file_name = args.name

    print("[ INFO ] - Got server port: {}".format(server_port))
    print("[ INFO ] - Got source file path: {}".format(source_file_path))
    print("[ INFO ] - Got file name: {}".format(file_name))

    print("[ INFO ] - Reading file: {}".format(args.name))
    read_file(source_file_path + "/" + file_name)
    print("[ SUCCESS ] - Finish reading file: {}".format(args.name))

    return 0


main()
