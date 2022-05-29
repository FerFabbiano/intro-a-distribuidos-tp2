from threading import Thread

from fs_server import FSServer


HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)


def main():
    fsServer = FSServer(HOST, PORT)

    thread = Thread(target=fsServer.run)
    thread.start()
    userInput = input()

    while userInput != "q":
        userInput = input()

    fsServer.stop()

    print("[ INFO ] - Termine de correr")
    thread.join()
    print("[ INFO ] - Join del server")


if __name__ == "__main__":
    main()
