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
    logging.info("[INFO] Se esta iniciando el servidor en el host : {} y port: {}".format(
        args.host, int(args.port)))
    thread = Thread(target=fsServer.run)
    thread.start()
    userInput = input()

    while userInput != "q":
        userInput = input()

    logging.info("[INFO] - Servidor ha sido frenado")
    fsServer.stop()

    thread.join()
    logging.info("[INFO] - El servidor ha finalizado exitosamente")
    logging.debug("[DEBUG] - Servidor ha joineado y termino de correr")


if __name__ == "__main__":
    main()
