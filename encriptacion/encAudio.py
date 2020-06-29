#from socket import socket, error
from socket import socket, error
import os
import logging
from  string import ascii_lowercase, ascii_uppercase


SERVER_ADDR = '167.71.243.238'
SERVER_PORT = 9822
BUFFER_SIZE = 64 * 1024

class arch(object):
    def Encriptacion(texto, pasos):
            resultado = []

            for i in texto:
                if i in ascii_lowercase:
                    indice = ascii_lowercase.index(i)
                    nuevo_indice = (indice + pasos) % len(ascii_lowercase) 
                    resultado.append(ascii_lowercase[nuevo_indice])
                elif i in ascii_uppercase:
                    indice = ascii_uppercase.index(i)
                    nuevo_indice = (indice + pasos) % len(ascii_uppercase) 
                    resultado.append(ascii_uppercase[nuevo_indice])
                else:
                    resultado.append(i)

            return ''.join(resultado)

    def enviar2():   
        sock = socket()
        sock.connect((SERVER_ADDR, SERVER_PORT))                     
        #funcion a llamar para enviar audios
        f=open("enviado.wav", "rb")             #abrimos el archivo como f
        fileContent = f.read()                  #luego almacenamos en filecontent
        f.close()
        byteArray = bytearray(fileContent)  
            #ingresamos el contenido en bytearray
        a=str(byteArray)
        
        b = arch.Encriptacion(a,1)
        print(b)
        sock.send(byteArray)
        sock.close()
        #lo publicamos con el destino dado
        print("----Audios Enviado-----")

    def grabar(dur):                        #funcion a llamar para grabar audios
        logging.basicConfig(
            level = logging.DEBUG, 
            format = '%(message)s'
            )

        logging.info('****COMIENZA LA GRABACION****')
        os.system('arecord -d '+str(dur)+ ' -f U8 -r 8000 enviado.wav')

        logging.info('------Grabacion finalizada, inicia reproduccion')
        os.system('aplay enviado.wav')


duracion = input('------Ingrese la duracion del audio(Seg.): ')     #pedimos el tiempo de grabacion
arch.grabar(duracion)            #llamamos funcion grabar con el valor de duracion
arch.enviar2()        #Luego de grabar enviamos el audio

