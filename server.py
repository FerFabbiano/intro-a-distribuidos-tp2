from threading import Thread
import logging
from server.fs_server import FSServer
from client.client_utils import build_server_parser


def main():

    args = build_server_parser().parse_args()
    fsServer = FSServer(args.host, int(args.port), args.dirpath)

    logging.basicConfig(
        format='%(asctime)s - %(message)s', datefmt='%H:%M:%S',
        level=args.loglevel)
    thread = Thread(target=fsServer.run)
    thread.start()
    userInput = input()

    while userInput != "q":
        userInput = input()

    fsServer.stop()

    logging.info("[INFO] - Servidor termino de correr")
    thread.join()
    logging.debug("[DEBUG] - Servidor termino de correr")


if __name__ == "__main__":
    main()
