import socket
from time import sleep

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65432  # The port used by the server
BUFFER_SIZE = 508

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
