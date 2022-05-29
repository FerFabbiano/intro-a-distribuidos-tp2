import socket
from time import sleep
import argparse


HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65432  # The port used by the server
BUFFER_SIZE = 508


def build_parser():
    my_parser = argparse.ArgumentParser()

    my_parser.add_argument("<command description>")
    my_parser.add_argument("-v", "--verbose", help="increase output verbosity")
    my_parser.add_argument("-q", "--quiet", help="decrease output verbosity")
    my_parser.add_argument("-H", "--host", help="server IP address")
    my_parser.add_argument("-p", "--port", help="server port", required=True)
    my_parser.add_argument("-s", "--src", help="source file path", required=True)
    my_parser.add_argument("-n", "--name", help="file name", required=True)

    # my_parser.add_argument("b", help="a second argument")

    # my_parser.add_argument("c", help="a third argument")

    # my_parser.add_argument("d", help="a fourth argument")

    # my_parser.add_argument("e", help="a fifth argument")

    # my_parser.add_argument(
    #     "-v", "--verbose", action="store_true", help="an optional argument"
    # )

    return my_parser


def main():
    my_parser = build_parser()
    args = my_parser.parse_args()

    print(args)

    return 0


main()

with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:

    # while(True):
    s.sendto(b"NCLIENTE NUEVO", (HOST, PORT))
    sleep(100000)
    # (recvData, serverAddress) = s.recvfrom(BUFFER_SIZE)

    # print("[ PROTOCOL ACK ] - ", str(recvData))

    # Poner validacion de que solo el servidor me mande mensajes

    # s.sendto(b"C", (HOST, PORT))
    # (recvData, serverAddress) = s.recvfrom(BUFFER_SIZE)

    # print("[ PROTOCOL ACK ] - ", str(recvData))


# print(f"Received {data!r}")
