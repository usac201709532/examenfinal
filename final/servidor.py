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
from socket import SHUT_RDWR
servi = '167.71.243.238'
SERVER_ADDR = ''
SERVER_PORT = 9822
BUFFER_SIZE = 64 * 1024
alives = []
cont = []
c=0
carne=''
inicio =0


class Comandos():
    def __init__(self, comando):
        self.comando = comando
        #self.detectar(l1)

    def detectar(self,comando,client,topic):
        if comando[3:6] == 'x04': 
            carne = comando[6:15]
            self.Alive(carne,client) 
        if comando[3:6] == 'x03':
            destino = comando.split('$')[1]
            tamaño = comando.split('$')[2]
            emisor = topic[12:]
            self.FTR(destino,tamaño,emisor,client)
            print(self.vec)

    def FTR(self,destino,tamaño,emisor,client):
        destinos=[]                     #para almacenar los usuarios en salas
        receptores = []                 #para almacenar a quiener se les mandara FRR
        if (len(destino)<=6):
            f = open("salasser","r")               
            while(True):
                linea = f.readline()
                info = linea.split(',')
                if(destino in info):
                    destinos.append(info[0])
                if not linea:
                    break    
            f.close()
            cont = 0
            for i in range(len(destinos)):
                if destinos[i] in self.vec:
                    print('FTR Es en sala activo')
                    receptores.append(destinos[i])
                    cont=cont+1
            if cont>0 :
               self.OK(emisor,client,receptores,tamaño)
            else:
                self.NO(emisor,client)


        else:
            if destino in self.vec:
                print('FTR Es usuario activo')
                receptores.append(destino)
                self.OK(emisor,client,receptores,tamaño)
            else:
                self.NO(emisor,client)

    def NO(self,emisor,client):
        emisr = str(emisor).encode()
        No = b'\x07' + b'$' + emisr        
        client.publish('comandos/22/'+ emisor, No)
        print('NO fue publicado')

    def OK(self,emisor,client,receptores,tamaño):
        emisr = str(emisor).encode()
        Ok = b'\x06' + b'$' + emisr
        print(emisor)
        client.publish('comandos/22/'+ emisor, Ok)
        print('Ok fue publicado')
        self.recvaudio(client,receptores,emisor,tamaño) 
        

    def Alive(self, usr,client):   
        if usr in alives:
            pos = alives.index(usr)
            cont[pos] = cont[pos] + 1

        else:
            alives.append(usr)
            cont.append(1)
            inicio=0

        def vivos():
            while True:
                c=0 
                while (c <= 3):
                    c = c +1
                    #print(str(c))
                    time.sleep(2) 
                if (c >= 3):
                    for i in range(len(alives)):
                        if(cont[i]==0):
                            alives.pop(i)
                            cont.pop(i)
                            print('borrado')
                        else:
                            cont[i]=0 
                            print('reseteado')  
                    c=0  
                    print(alives)  
                    print("estos son activos")
                    #client.publish('usuarios/22/201701026', 'Activo')
                    self.ACK(alives,client)            
        if (inicio == 0):          
            vivo = threading.Thread(name = 'Alives', target = vivos,daemon = True)
                #Luego de configurar cada hilo, se inicializan
            vivo.start()   
            self.inicio = 1

    def ACK(self,activ,client):
        self.vec = activ
        if (len(self.vec)):
            for i in range(len(self.vec)):
                idee = str(self.vec[i]).encode()
                akc = b'\x05' + b'$' + idee
                client.publish('comandos/22/'+self.vec[i], akc)

    def recvaudio(self,client,receptores,emisor,tamaño):
        def recibiraudio():
            server_socket = socket()
            server_socket.bind((SERVER_ADDR, SERVER_PORT))
            server_socket.listen(100) #1 conexion activa y 9 en cola
            
            conn, addr = server_socket.accept()
            audior = open("servi.wav", "wb")

            while True:
                try:
                    input_data = conn.recv(40*1024) #Aca se guarda el archivo entrante
                except error:
                    pirnt("Error de lectura")
                    break
                else:
                    if input_data:
                        if isinstance(input_data, bytes):
                            end = input_data[0] == 1
                        else:
                            end = input_data == chr(1)
                        if not end:
                            audior.write(input_data)
                        else:
                            break
                        print("Se ha recibido el archivo")
                        print('cerrando servidor')
                        server_socket.shutdown(SHUT_RDWR)
                        audior.close()
                        server_socket.close()
                        self.FRR(client,receptores,emisor,tamaño)
            audior.close()
            server_socket.close()
        
        au = threading.Thread(name = 'audio hilo', target = recibiraudio,daemon = True)
        #Luego de configurar cada hilo, se inicializan
        au.start() 

    def FRR(self,client,receptores,emisor,tamaño):
        emisr = str(emisor).encode()
        tam = str(tamaño).encode()
        FRR = b'\x02' + b'$' + emisr + b'$' + tam
        print('Esto son los receptores'+ str(receptores))
        for i in range(len(receptores)):
            client.publish('comandos/22/'+str(receptores[i]), FRR ) 
        self.enviarAu()

    def enviarAu(self):
        def envrau():
            
            server_socket = socket()
            #server_socket.bind((SERVER_ADDR, SERVER_PORT))
            server_socket.listen(100) #1 conexion activa y 9 en cola
            print("\nEsperando conexion remota...\n")
            conn, addr = server_socket.accept()
            try:
                while True:
                    print('Conexion establecida desde ', addr)
                    print('Enviando Audio...')

                    audio = open('servi.wav', 'rb') 
                    archivo = audio.read(64*1024)
                    while archivo:
                        conn.sendfile(audio)
                        archivo = audio.read(64*1024)
                    audio.close()
                    conn.close()
                    print("\n\nArchivo enviado a: ", addr)
                    break
            finally:
                print("Cerrando el servidor...")
                server_socket.close()        
        envau = threading.Thread(name = 'audio hilo enviar', target = envrau,daemon = True)
        #Luego de configurar cada hilo, se inicializan
        envau.start()  

class Servidor(Comandos):
    def __init__(self, subs, destino):
        self.subs = subs
        self.destino = destino

    def conecmqtt(self):
        qos =2
        inicio = 0
        client = mqtt.Client(clean_session=True)
        client.on_message = self.on_message
        client.username_pw_set(MQTT_USER, MQTT_PASS)
        client.connect(host = MQTT_HOST, port = MQTT_PORT)
        client.subscribe([("comandos/22/201742012", qos), ("comandos/22/201701026", qos), ("comandos/22/201709532", qos), ("comandos/22", qos)])
        self.recibir(client)

    def recibir(self,client):
        self.c=0
        def recibir():
            while True:
                client.loop_start()  
                #print('recibiendo')
                time.sleep(1) 

                
        req = threading.Thread(name = 'Requests de Usuarios', target = recibir,daemon = True)
        #Luego de configurar cada hilo, se inicializan
        req.start()   
        print('esperando....')     
        while True:
            x=1

    def on_message(self, client, userdata, msg):
        ##print("Ha llegado el mensaje al topic: " + str(msg.topic))   #Se muestra en pantalla informacion que ha llegado
        #print("El contenido del mensaje es: " + str(msg.payload))
        comando = []
        comando = str(msg.payload)
        topic = str(msg.topic)
        self.detectar(comando,client,topic)



        



class Inicio(Servidor):
        def __init__(self):
            self.conecmqtt()



Inicio()