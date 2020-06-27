import paho.mqtt.client as mqtt
import logging
import time
import os
import logging
import datetime #Para generar fecha/hora actual
import binascii
import threading #Concurrencia con hilos
from socket import socket
from broker import * #Informacion de la conexion

SERVER_ADDR = ''
SERVER_PORT = 9822
BUFFER_SIZE = 64 * 1024



class menudelameraverga():
    def __init__(self, id):
        self.id = id
        self.destino = ''
        self.mensaje = ''
        self.n = 0

    def ejec(self):



        print("BIENVENIDO CLIENTE " + self.id)


        client = mqtt.Client(clean_session=True)
        client.on_message = self.on_message


        client.username_pw_set(MQTT_USER, MQTT_PASS)
        client.connect(host = MQTT_HOST, port = MQTT_PORT)
        client.subscribe(self.id)
        #subcripcion a Usuario
        g = open("usuario.txt","r")
        while(True):
            linea = g.readline()
            linea = linea[:9]
            if not linea:
                break    
            client.subscribe('usuarios/22/'+linea)
        g.close()        
        
        #Subscripciones a salas 
        f = open("salas.txt","r")
        while(True):
            linea = f.readline()
            linea = linea[:5]
            if not linea:
                break    
            client.subscribe('salas/'+linea[:2]+'/'+linea[2:])
        f.close()



        FTR = b'\x04'
        ida = self.id.encode("utf-8")
        FTR = FTR + ida 
        def contador(rango = range(2000), delay = 2):
            for i in rango:
                client.publish('200', '201701026')
                #print("contadpor : "+ str(i))
                time.sleep(delay) #Delay en segundos

        t1 = threading.Thread(name = 'Contador 1 seg', target = contador, args = (range(100), ), daemon = True
                            )
        #Luego de configurar cada hilo, se inicializan
        t1.start()

        def recibir():
            sock = socket()
            sock.connect((SERVER_ADDR, SERVER_PORT))
            try:
                buff = sock.recv(BUFFER_SIZE)
                archivo = open("recib.wav", "wb") #Aca se guarda el archivo entrante
                while buff:
                    buff = sock.recv(BUFFER_SIZE) #Los bloques se van agregando al archivo
                    archivo.write(buff)

                archivo.close() #Se cierra el archivo

                print("Recepcion de archivo finalizada")

            finally:
                print('Conexion al servidor finalizada')
                sock.close() #Se cierra el socket

        def enviar():
            sock = socket()
            sock.connect((SERVER_ADDR, SERVER_PORT))
            
            while True:
                print("Enviando Audio...")
                audio = open('enviado.mp3', 'rb') 
                archivo = audio.read(64*1024)
                while archivo:
                    sock.send(archivo)
                    archivo = audio.read(64*1024)
                break
            try:
                sock.send(chr(1))
            except TypeError:
                sock.send(bytes(chr(1), "utf-8"))
            audio.close()
            sock.close()
            print("Archivo Enviado")
            print("Cerrando el servidor...")

        def grabar(dur):
            logging.basicConfig(
                level = logging.DEBUG, 
                format = '%(message)s'
                )

            logging.info('Comenzando grabacion')
            os.system('arecord -d '+str(dur)+ ' -f U8 -r 8000 enviado.mp3')

            logging.info('Grabacion finalizada, inicia reproduccion')
            os.system('aplay enviado.mp3')



        while True:

            client.publish('hola', "alive")

            while True:
                self.n=0
                print("Que desea?")
                print("1. Enviar Texto")
                print("2. Enviar Audio")     
                print("4. Salir")
                menu1 = input("que desea?: ")
                
                if(menu1 == '1'):
                    print("------MENSAJE DE TEXTO------")
                    print("     1. Enviar a Usuario")
                    print("     2. Enviar a Sala")
                    menu2 = input("     que desea?: ")
                    
                    if(menu2 == '1'):
                        print("------A USUARIO------")
                        while self.n != 1:
                            self.destino = input("Ingrese Id Usuario a mandar MSM: usuarios/22/:")
                            if(len(self.destino) != 9):
                                print("Usuario invalido!!! Vuelva a ingresar")
                                self.n =0
                            else:
                                self.n =1
                        self.destino = 'usuarios/22/' + self.destino 
                        msm = input("escribe y manda...")
                        msm = "@"+self.id+": "+ msm
                        client.publish(self.destino, msm)

                    if(menu2 == '2'):
                        print("------A SALA------")
                        while self.n !=1:
                            self.destino = input("Ingrese la sala: salas/22/S:")
                            if(len(self.destino) != 2):
                                print("Sala invalida!!! Vuelva a ingresar")
                                self.n =0
                            else:
                                self.n =1
                        self.destino = 'salas/22/S' + self.destino
                        msm = input("escribe y manda...")
                        msm = "@"+self.id+": "+ msm
                        client.publish(self.destino, msm)

                if(menu1 == '2'):
                    print("------MENSAJE DE VOZ------")
                    print("     1. Enviar a Usuario")
                    print("     2. Enviar a Sala")
                    menu2 = input("     que desea?: ")
                    if(menu2 == '1'):
                        print("------A USUARIO------")
                        while self.n != 1:
                            self.destino = input("Ingrese Id Usuario a mandar MSM: usuarios/22/:")
                            if(len(self.destino) != 9):
                                print("Usuario invalido!!! Vuelva a ingresar")
                                self.n =0
                            else:
                                self.n =1
                        self.destino = 'usuarios/22/' + self.destino 
                        duracion = input('------Ingrese la duracion del audio(Seg.): ')
                        grabar(duracion)
                        enviar()


                    if(menu2 == '2'):
                        print("------A SALA------")
                        while self.n !=1:
                            self.destino = input("Ingrese la sala: salas/22/:")
                            if(len(self.destino) != 4):
                                print("Sala invalida!!! Vuelva a ingresar")
                                self.n =0
                            else:
                                self.n =1
                        self.destino = 'salas/22/' + self.destino
                        duracion = input('------Ingrese la duracion del audio(Seg.): ')
                        grabar(duracion)
                        enviar()


                    FTR = b'\x03'
                    tam = b'123'
                    ida = self.id.encode("utf-8")
                    FTR = FTR + ida + tam
                    print(FTR[3])
                    print('\n\nEnviando request al servidor')

                if(menu1 == '3'):   
                    print("Nuevos Mensajes: ")
                    print("-----Hora/Fecha --------  Usuario----- MSM---")
                    client.loop_start()
                    time.sleep(1)
                    client.loop_stop()

                if(menu1 == '4'):
                    exit() 

                if(menu1 == '5'):
                    recibir()
                    os.system('aplay recib.wav')


                break



    def on_message(self, client, userdata, msg):
    #Se muestra en pantalla informacion que ha llegado
        print("--------------------------------")
        print(str(datetime.datetime.now().ctime()) + ": " +str(msg.payload.decode("utf-8")))
        print("--------------------------------")
        
deunavariable = menudelameraverga('201701026')

deunavariable.ejec()


