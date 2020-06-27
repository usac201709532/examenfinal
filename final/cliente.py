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

class Cliente: 
    def __init__(self, subs, destino):
        self.subs = subs
        self.destino = destino


    def conecmqtt(self):
        client = mqtt.Client(clean_session=True)
        client.on_message = self.on_message
        client.username_pw_set(MQTT_USER, MQTT_PASS)
        client.connect(host = MQTT_HOST, port = MQTT_PORT)
        self.subscribir(client)

    def subscribir(self,client):                                    # Funcion para subcrcibir a todos los topicos
        g = open("usuario","r")                     #Se abre el archivo en donde esta el usuario
        while(True):
            linea = g.readline()
            linea = linea[:9]                        #guardamos en linea el carne o ID
            if not linea:
                break    
            print("----------------------------- ")
            print("BIENVENIDO CLIENTE " + linea)      #Al menu le damos la bienvenida al ID
            self.id = linea                             #guardamos el id para usarlo luego
            client.subscribe('usuarios/22/'+linea)        #Subscribimos a usarios y audios
            client.subscribe('audio/22/'+linea)
        g.close()        
        #Subscripciones a salas 
        f = open("salas","r")                               #el mismo procedimeinto para salas de conver.
        while(True):
            linea = f.readline()
            linea = linea[:5]
            if not linea:
                break    
            client.subscribe('salas/'+linea[:2]+'/'+linea[2:])
            client.subscribe('audio/'+linea[:2]+'/'+linea[2:])
        f.close()
        #client.subscribe("comandos/22/"+ self.id)

        def recibir():
            while True:
                client.loop_start()  
                #print('recibiendo')
                time.sleep(1) 

        t1 = threading.Thread(name = 'Contador 1 seg', target = recibir,daemon = True)

        #Luego de configurar cada hilo, se inicializan
        t1.start()

        FTR = b'\x04201701026' 
        def ALIVE():
            while True:
                client.publish('comandos/22/201701026', FTR)
                #print("contadpor : "+ str(i))
                time.sleep(2) #Delay en segundos

        alive = threading.Thread(name = 'ACtivo', target = ALIVE, daemon = True)
        #Luego de configurar cada hilo, se inicializan
        alive.start()

        self.menu(client)
        
    def menu(self,client):
        while True:
            n = 0
            self.menu3 = '0'
            self.menu1 = '0'
            self.menu2 = '0'
            print("---------------------------- ")          #JFMB comenzamos lanzado un menu con las opciones
            print("Que desea?")
            print("1. Enviar Texto")
            print("2. Enviar Audio")    
            print("5. Salir")
            self.menu1 = input("que desea?: ")                   #JFMB ingresamos en menu1 la eleccion del usuario
            if(self.menu1 == '1'):                               #JFMB Op.1 enviar texto a Usuario o Sala
                print("------MENSAJE DE TEXTO------")
                print("     1. Enviar a Usuario")
                print("     2. Enviar a Sala")
                self.menu2 = input("     que desea?: ")

                if(self.menu2 == '1'):                           #JFMB Si es usuario...
                    print("------A USUARIO------")
                    while n != 1:                      #JFMB Pedimos que ingrese un usuario hasta que cumpla con el tamaño de un carne
                            destino = input("Ingrese Id Usuario a mandar MSM: usuarios/22/:")
                            if(len(destino) != 9):
                                print("Usuario invalido!!! Vuelva a ingresar")      #si no cumple con el tamaño no es valido
                                n = 0
                            else:
                                n = 1
                    destino = 'usuarios/22/' + destino
                    self.menu3 = '1'
                    self.enviartxt(client,destino)

                if(self.menu2 == '2'):                       #JFMB lo mismo en sala...
                    print("------A SALA------")
                    while n !=1:
                        destino = input("Ingrese la sala: salas/22/S:") #JFMB el usr debe ingresar el No. de sala
                        if(len(destino) != 2):
                            print("Sala invalida!!! Vuelva a ingresar")
                            n =0
                        else:
                            n =1
                    destino = 'salas/22/S' + destino
                    self.menu3 = '1'
                    self.enviartxt(client,destino)    

            if(self.menu1 == '2'):
                print("------MENSAJE DE VOZ------")
                print("     1. Enviar a Usuario")
                print("     2. Enviar a Sala")
                self.menu2 = input("     que desea?: ")
                if(self.menu2 == '1'):
                    print("------A USUARIO------")
                    while n != 1:
                        destino = input("Ingrese Id Usuario a mandar MSM: usuarios/22/:")
                        if(len(destino) != 9):
                            print("Usuario invalido!!! Vuelva a ingresar")
                            n =0
                        else:
                            n =1
                    destino = 'usuarios/22/' + destino 
                    self.menu3 = '1'
                    duracion = input('------Ingrese la duracion del audio(Seg.): ')
                    self.enviaraudio(client,destino,duracion)

                if(self.menu2 == '2'):
                    print("------A SALA------")
                    while n !=1:
                        destino = input("Ingrese la sala: salas/22/:")
                        if(len(destino) != 4):
                            print("Sala invalida!!! Vuelva a ingresar")
                            n =0
                        else:
                            n =1
                    destino = 'salas/22/' + destino
                    self.menu3 = '1'
                    duracion = input('------Ingrese la duracion del audio(Seg.): ')
                    self.enviaraudio(client,destino,duracion)

    def enviartxt(self, client, destino):
        msm = input("escribe y manda...")
        #msm = "@"+self.id+": "+ msm                   #JFMB se le agrega sel ID al msm para que el receptor sepa quien lo envia
        client.publish(destino, msm)       #JFMB publicamos la info al destino
        print("-------Enviado--------- ")
    
    def enviaraudio(self, client, destino,duracion):
        logging.basicConfig(level = logging.DEBUG, format = '%(message)s')
        logging.info('Comenzando grabacion')
        os.system('arecord -d '+str(duracion)+ ' -f U8 -r 8000 enviado.mp3')
        logging.info('Grabacion finalizada, inicia reproduccion')
        os.system('aplay enviado.mp3')      
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

    def on_message(self, client, userdata, msg):
        print("\n --------NUEVO MENSJAE!----------")
        print(str(datetime.datetime.now().ctime()) + ": " +str(msg.payload.decode("utf-8")))
        print("--------------------------------")
        if (self.menu1 == '0' and self.menu2 =='0'):
            print("Que desea?")
            print("1. Enviar Texto")
            print("2. Enviar Audio")    
            print("3. Salir")
        elif (self.menu1 == '1' and self.menu2 =='0'):
            print("------MENSAJE DE TEXTO------")
            print("     1. Enviar a Usuario")
            print("     2. Enviar a Sala")            
            print("Que desea?")   
        elif (self.menu1 == '2' and self.menu2 =='0'):
            print("------MENSAJE DE AUDIO------")
            print("     1. Enviar a Usuario")
            print("     2. Enviar a Sala")            
            print("Que desea?")  
        elif (self.menu1 == '1' and self.menu2 =='1' and self.menu3 == '0') :
            print("------MENSAJE DE TEXTO A USUARIO------")
            print("Ingrese Id Usuario a mandar MSM: usuarios/22/:")
        elif (self.menu1 == '1' and self.menu2 =='1' and self.menu3 == '1') :
            print("------MENSAJE DE TEXTO A USUARIO------")
            print("Escriba mesnaje y mande:")
        elif (self.menu1 == '1' and self.menu2 =='2' and self.menu3 == '0') :
            print("------MENSAJE DE TEXTO A SALA------")
            print("Ingrese la sala: salas/22/S:")
        elif (self.menu1 == '1' and self.menu2 =='2' and self.menu3 == '1') :
            print("------MENSAJE DE TEXTO A SALA------")
            print("Escriba mesnaje y mande:")    
        elif (self.menu1 == '2' and self.menu2 =='1' and self.menu3 == '0') :
            print("------MENSAJE DE AUDIO A USUARIO------")
            print("Ingrese Id Usuario a mandar MSM: usuarios/22/:")
        elif (self.menu1 == '1' and self.menu2 =='1' and self.menu3 == '1') :
            print("------MENSAJE DE AUDIO A USUARIO------")
            print("Escriba la duracion de grabacion en segundos:")                    
        elif (self.menu1 == '2' and self.menu2 =='2' and self.menu3 == '0') :
            print("------MENSAJE DE AUDIO A SALA------")
            print("Ingrese la sala: salas/22/S:")
        elif (self.menu1 == '1' and self.menu2 =='2' and self.menu3 == '1') :
            print("------MENSAJE DE AUDIO A SALA------")
            print("Escriba la duracion de grabacion en segundos:")                      
        



class Inicio(Cliente):
    def __init__(self):
        self.conecmqtt()
Inicio()
