SERVER   -   CLIENT

---- < Dar de alta>  ---

us / uc/ ds /dc

1er mensaje
1 bit operation: 0 si es download, 1 si es upload.
508 bytes -

CL-SR Handshake upload
1 byte de op code
4 bytes de largo de archivo
1 byte para largo del nombre del archivo
<nombre del archivo>

SR-CL ACCEPTED HANDSHAKE
1 byte de op code
2 bytes para el id que tiene que mandar.

CL-SR UPLOAD PROCESS
1 byte de op code.
2 bytes de id de archivo.
4 bytes para el sequence number.
2 bytes para el largo del payload.
<dynamic payload>

SR-CL ACCEPTED UPLOAD MSG
1 byte de op code
4 bytes del ultimo sequence number que recibimos.


<--- APLIC comn PROT ---> 

instance = FileTransfer.initUpload('IP', 'nombredelarchivo', 'tamañoarchivo');

resp = instance.waitForResponse();

resp.succesfull == ok  {
    instance.sendFileSegment('tamaño del segmento', el segmento);
}








CL-SR Handshake downlaod
1 byte de op code
1 byte para largo del nombre del archivo
<nombre del archivo>



[U][FILE_NAME_LENGTH]
CLIENT "



TRANSPORTE


0, 1, 2, 3
<sequence_number><paquet_length><paquet_payload>


socketNuestro.send(500)
CL -> SR
0, 500, <contenido>
LOST

CL -> SR
0, 500, <contenido>

SR-> CL
-> contenido a la capa de apl.
ACK, 0

socketNuestro.send(500)
1, 500, <contenido>
500

CLI - SRV
transport = TransportInit(IP, PORT)

SRV - CLI
Ok lo recibi, conexion establecida

CLI-SRV
-1
// Me tiene que devolver o 512, si envio todo el contenido bien, o -1 si no pudo enviarlo.
// No va a poder enviarlo si el servidor muere
bytes_recv = transport.send(512, contenido).
muere servidor.

// Me tiene que devolver lo que recibio, y como aplicacion lo interpreto
bytes_recibidos = transport.recv(512)



