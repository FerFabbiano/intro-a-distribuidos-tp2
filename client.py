from time import sleep
from transport_tpc.connection import Connection

HOST = "127.0.0.1"  # The server's hostname or IP address
PORT = 65433  # The port used by the server
BUFFER_SIZE = 508


def main():
    # while(True):
    # s.sendto(b"NCLIENTE NUEVO", (HOST, PORT))
    connection = Connection.connect(HOST, PORT)
    print("[ NUEVA CONEXION ]")
    sleep(100000)
    # (recvData, serverAddress) = s.recvfrom(BUFFER_SIZE)

    # Poner validacion de que solo el servidor me mande mensajes

    # s.sendto(b"C", (HOST, PORT))
    # (recvData, serverAddress) = s.recvfrom(BUFFER_SIZE)

    # print("[ PROTOCOL ACK ] - ", str(recvData))


main()
# print(f"Received {data!r}")
