import socket

HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)
CHUNK_SIZE = 1024

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST, PORT))
    s.listen()
    conn, addr = s.accept()
    with conn:
        print(f"Connected by {addr}")
        while True:
            data = conn.recv(CHUNK_SIZE)
            if not data:
                break
            conn.sendall(data)

# Protocolo aplicación
"""
python upload.py -s path_en_cliente.mp3 -n nombre_o_path_en_servidor.mp3
python download.py -n nombre_o_path_en_servidor.mp3 -d path_en_cliente.mp3

Upload: nombre de archivo, tamaño de archivo
Download: nombre de archivo

Ej cargar un archivo:
>> HOLA_CLIENTE
<< HOLA_SERVIDOR

>> UPLOAD nombre_o_path_en_servidor.mp3, 2MB
<< OK

>> {2MB of binary data}
<< OK

>> DOWNLOAD nombre_o_path_en_servidor.mp3
<< OK, 2MB, {2MB of binary data}

>> CHAU_CLIENTE
{conexion cerrada por el cliente} (SHUT_WR)
<< CHAU_SERVIDOR
{conexion cerrada por el servidor} (SHUT_RDWR)



enum Message {
    HolaCliente,
    HolaServidor,
    Upload(nombre: String, size: usize),
    Download(nombre: String),
    ChauCliente,
    ChauServidor,
}

enum Response {
    Ok,
    OkDownload(size: usize),
}

conn.recv<Message>()
conn.recv(2mb)

"""

# class ByteStream:
#     @abstractmethod
#     def connect():
#         pass

#     @abstractmethod
#     def send_bytes():
#         pass

#     @abstractmethod
#     def recv_bytes():
#         pass

#     @abstractmethod
#     def close():
#         pass


# def accept_tcp(host, port, backlog):
#     s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     s.bind((host, port))
#     s.listen(backlog)

#     while True:
#         lanzar_hilo(ByteStreamTcp(s.accept()))


# import struct

# struct.pack("iii", (1, 2, 3))
# struct.unpack("iii") -> (1, 2, 3)

# class ByteStreamTcp(ByteStream):
#     @staticmethod
#     def connect(host, port):
#         s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         s.connect((host, port))
#         return ByteStreamTcp(s)

#     def __init__(self, socket):
#         self.s = socket

#     def send_bytes(self, data):
#         self.s.send(data)  # ver si envia TODA la data o una parte

#     def recv_bytes(self, quantity):
#         return self.s.recv(quantity)  # ver si recibe exactamente quantity bytes o
#                                          como maximo qty bytes.

#     def close(self):
#         self.s.close()


# class ByteStreamSelectiveRepeat(ByteStream):
#     def connect():
#         ???
#     def send_bytes(bytes):
#         ??
#     def recv_bytes(quantity):
#         ??
#     def close():
#         ??


# class ByteStreamStopNWait(ByteStream):
#     def connect():
#         ???
#     def send_bytes(bytes):
#         ??
#     def recv_bytes(quantity):
#         ??
#     def close():
#         ??


# Protocolo transporte

"""
- Definir mensajes (aplicación) [hecho]
- Ver como serializar los mensajes / Definir protocolo binario
    (id, length, payload = ILP)
- Aceptar conexiones / múltiples hilos / joins / etc
- Storear archivos / leer archivos de algun lado
- Implementar ByteStream + Accept TCP
- Implementar ByteStream + Accept Stop & Wait
- Implementar ByteStream + Accept Selective repeat
"""
