from threading import Thread
import logging
from server.fs_server import FSServer


HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65434  # Port to listen on (non-privileged ports are > 1023)


def main():
    fsServer = FSServer(HOST, PORT)

    logging.basicConfig(
        format='%(asctime)s - %(message)s', datefmt='%H:%M:%S',
        level=logging.DEBUG)
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
