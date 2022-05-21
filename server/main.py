from threading import Thread
import socket

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

class Server:

    def __init__(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        s.listen()
        conn, addr = s.accept()

        with conn:
        print(f"Connected by {addr}")
        while True:
            data = conn.recv(CHUNK_SIZE)
            if not data:
                break
            conn.sendall(data)

    def run():

        while True:
            pass

    def stop_running():
        


def main():
    

    # Corro el servidor en un hilo aparte
    # Server server;
    # server.run();
    thread = Thread(target = run)
    thread.start()
    userInput = input()

    while (userInput != 'q'):
        userInput = input()

    thread.join()
    #server.stop_running();
    #server.join();
if __name__ == '__main__':
    main()