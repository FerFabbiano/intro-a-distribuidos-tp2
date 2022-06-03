# intro-a-distribuidos-tp2
Repositorio para el Trabajo Práctico 2 de la materia Introducción a los sistemas distribuidos de FIUBA


## Comandos

#### Correr el servidor



e.g: python server.py  -H 127.0.0.1 -p 65434 -s files

#### Hacer un upload desde un cliente

e.g: python upload.py -H 127.0.0.1 -p 65434 -s ./example_files/upload.txt -n upload.txt

#### Hacer un download desde un cliente

e.g: python download.py -H 127.0.0.1 -p 65434 -d files/upserver.txt -n upload.txt -v
