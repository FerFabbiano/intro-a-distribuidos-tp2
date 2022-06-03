# intro-a-distribuidos-tp2
Repositorio para el Trabajo Práctico 2 de la materia Introducción a los sistemas distribuidos de FIUBA


## Comandos

### Se tienen que ejecutar dentro de la carpeta src/

#### Correr el servidor

python3 start-server.py [-h] [-v │ -q] [-H ADDR] [-p PORT] [-s DIRPATH]

*e.g: python3 start-server.py  -H 127.0.0.1 -p 65434 -s files*

#### Hacer un upload desde un cliente

python3 upload.py [-h] [-v │ -q] [-H ADDR] [-p PORT] [-s FILEPATH] [-n FILENAME]

*e.g: python3 upload.py -H 127.0.0.1 -p 65434 -s ../files_to_upload_client/upload.txt -n upload.txt*

#### Hacer un download desde un cliente

python3 download.py [-h] [-v │ -q] [-H ADDR] [-p PORT] [-s FILEPATH] [-n FILENAME]

*e.g: python3 download.py -H 127.0.0.1 -p 65434 -d ../files_downloaded_client/upserver.txt -n upload.txt*


### Cambiar a stop&wait

En la carpeta src/transport se encuentra un archivo "rdt_controller.py" que determina si se ejecutara selective repeat o stop&wait, en el caso que se quiera ejecutar el stop&wait hay que establecerlo como DefaultRdtController
