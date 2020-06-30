#from socket import socket, error
from socket import socket, error
import os
import logging
from  string import ascii_lowercase, ascii_uppercase
import base64

SERVER_ADDR = '167.71.243.238'
SERVER_PORT = 9822
BUFFER_SIZE = 64 * 1024

class arch(object):
    def recibir2():
        sock = socket()
        sock.connect((SERVER_ADDR, SERVER_PORT))

        try:
            buff = sock.recv(BUFFER_SIZE)
            archivo = open('recibido.wav', 'wb') #Aca se guarda el archivo entrante
            while buff:
                archivo.write(buff)
                buff = sock.recv(BUFFER_SIZE) #Los bloques se van agregando al archivo

            archivo.close() #Se cierra el archivo
            print("Recepcion de archivo finalizada")

        finally:
            print('Conexion al servidor finalizada')
            sock.close() #Se cierra el socket


    def enviar2():   
        sock = socket()
        sock.connect((SERVER_ADDR, SERVER_PORT))                     
        try:
            f=open("enviado.wav", "rb")             #abrimos el archivo como f
            fileContent = f.read()                  #luego almacenamos en filecontent
            f.close()
            byteArray = bytearray(fileContent) 
            print(byteArray)
            sock.send(byteArray)
            print("----Audios Enviado-----")
            
        finally:
            print('Conexion al servidor finalizada')
            sock.close()
            #lo publicamos con el destino dado
           

    def grabar(dur):                        #funcion a llamar para grabar audios
        logging.basicConfig(
            level = logging.DEBUG, 
            format = '%(message)s'
            )

        logging.info('****COMIENZA LA GRABACION****')
        os.system('arecord -d '+str(dur)+ ' -f U8 -r 8000 enviado.wav')

        logging.info('------Grabacion finalizada, inicia reproduccion')
        os.system('aplay enviado.wav')


duracion = input('Ingrese la duracion del audio: ')     #pedimos el tiempo de grabacion
arch.grabar(duracion)            #llamamos funcion grabar con el valor de duracion
arch.enviar2()        #Luego de grabar enviamos el audio

