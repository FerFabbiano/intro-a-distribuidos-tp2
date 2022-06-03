# intro-a-distribuidos-tp2
Repositorio para el Trabajo Práctico 2 de la materia Introducción a los sistemas distribuidos de FIUBA


## Comandos

#### Correr el servidor

python3 server.py [-h] [-v │ -q] [-H ADDR] [-p PORT] [-s DIRPATH]

e.g: python3 server.py  -H 127.0.0.1 -p 65434 -s files

#### Hacer un upload desde un cliente

python3 upload.py [-h] [-v │ -q] [-H ADDR] [-p PORT] [-s FILEPATH] [-n FILENAME]

e.g: python3 upload.py -H 127.0.0.1 -p 65434 -s ./example_files/upload.txt -n upload.txt

#### Hacer un download desde un cliente

python3 download.py [-h] [-v │ -q] [-H ADDR] [-p PORT] [-s FILEPATH] [-n FILENAME]

e.g: python3 download.py -H 127.0.0.1 -p 65434 -d files/upserver.txt -n upload.txt
