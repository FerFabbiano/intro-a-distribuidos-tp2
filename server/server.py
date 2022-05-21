from threading import Thread

from models import ByteStreamTcpServer

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)


def main():
    byteStreamTcpServer = ByteStreamTcpServer(HOST, PORT)

    thread = Thread(target=byteStreamTcpServer.run)
    thread.start()
    userInput = input()

    while userInput != "q":
        userInput = input()

    byteStreamTcpServer.stop_running()
    thread.join()


if __name__ == "__main__":
    main()
