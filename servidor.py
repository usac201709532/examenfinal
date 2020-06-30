#Jose Fernando Marticorena Barrientos
# Jonathan Mardoqueo Lorenzo Lopez

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


class Comandos():                              #CJFMBlase de Comandos
    def __init__(self, comando):
        self.comando = comando              
        #self.detectar(l1)

    def detectar(self,comando,client,topic):    #JFMB Metodo para ver que comando llega
        if comando[3:6] == 'x04':               #JFMB Si LLega el comando x04 Alive 
            carne = comando[6:15]
            self.Alive(carne,client)            #JFMB Nos conduce al metodo de usuarios activos con el argumento del id o carne del usuario
        if comando[3:6] == 'x03':               #JFMB si llema el comando x03 es el request de envio
            destino = comando.split('$')[1]
            tamaño = comando.split('$')[2]
            emisor = topic[12:]
            self.FTR(destino,tamaño,emisor,client) #JFMB nos dirije a metoroFRT con destino, tama;o de arch y el emisor como argumentos
            print(self.vec)

    def FTR(self,destino,tamaño,emisor,client): #JFMB metodo FTR
        destinos=[]                     #JFMB para almacenar los usuarios en salas
        receptores = []                 #JFMB para almacenar a quiener se les mandara FRR
        if (len(destino)<=6):
            f = open("salasser","r")        #JFMB utilizamos el archivo salaser para ver quiene estan en la sala        
            while(True):                    #JFMB while para leer el archivo
                linea = f.readline()
                info = linea.split(',')
                if(destino in info):
                    destinos.append(info[0])    #JFMB guardamos los usuarips de la sala
                if not linea:
                    break    
            f.close()
            cont = 0
            for i in range(len(destinos)):
                if destinos[i] in self.vec:          # JFMB aca vemos si el usuario esta activo
                    print('FTR Es en sala activo') 
                    receptores.append(destinos[i])  #JFMB ingresamos los usr activos
                    cont=cont+1
            if cont>0 :
               self.OK(emisor,client,receptores,tamaño)   #JFMB si hay mas de 0 usuarios activos vamos al metodo OK
            else:
                self.NO(emisor,client)      #JFMB sino al metodo No


        else:                               #sJFMB i solo se hizo el request para 1 usuario
            if destino in self.vec:             #JFMB verificamos si esta activo
                print('FTR Es usuario activo')
                receptores.append(destino)      #JFMB lo agregamos al cevtor de activos
                self.OK(emisor,client,receptores,tamaño)  #si activo Ok  
            else:
                self.NO(emisor,client)      #sino No

    def NO(self,emisor,client):         
        emisr = str(emisor).encode()
        No = b'\x07' + b'$' + emisr        
        client.publish('comandos/22/'+ emisor, No)  #JFMB publicamos al topic + el emisor del request el comando No
        print('NO fue publicado')

    def OK(self,emisor,client,receptores,tamaño):
        emisr = str(emisor).encode()
        Ok = b'\x06' + b'$' + emisr
        print(emisor)
        client.publish('comandos/22/'+ emisor, Ok)      #JFMB publicamos al topic + el emisor del request el comando Si
        print('Ok fue publicado')
        self.recvaudio(client,receptores,emisor,tamaño) #JFMB y vamos al metodo d recibir el audio
        

    def Alive(self, usr,client):   #JFMB metodo para marcar al usuario como alive
        if usr in alives:           #JFMBsi el usuario ya esta en el vector alives
            pos = alives.index(usr)     #vJFMB vemos en que posicion esta del vector
            cont[pos] = cont[pos] + 1   #JFMB y en un contador agregamos que nos llego su alive cada 2seg

        else:
            alives.append(usr)      #JFMB si no esta en la lista lo agregamos
            cont.append(1)      #JFMB y le ponemos 1 a su contador
            inicio=0
#empieza el hilo infinito para usr activos
        def vivos():
            while True:
                c=0 
                while (c <= 3):     #JFMB hacemos un ciclo infinito de 3 ciclos de 2 segundos(6seg)
                    c = c +1
                    #print(str(c))
                    time.sleep(2) 
                if (c >= 3):                    #JFMb si en esos 6 seg
                    for i in range(len(alives)):    #JFMB leemos todos los activos
                        if(cont[i]==0):             #JFMB el contador del usuario es 0
                            alives.pop(i)           #JFMB lo eliminamos y su contador tambien
                            cont.pop(i)
                            print('borrado')
                        else:
                            cont[i]=0               #JFMB si el contador el mayor a 0 lo reseteamos y sigue vivo
                            print('reseteado')  
                    c=0  
                    print(alives)               
                    print("estos son activos")
                    #client.publish('usuarios/22/201701026', 'Activo')
                    self.ACK(alives,client)   #JFMB vamos a AKC con la lista de activos         
        if (inicio == 0):                               #llamamos al hilo solo al empezar
            vivo = threading.Thread(name = 'Alives', target = vivos,daemon = True)
                #Luego de configurar cada hilo, se inicializan
            vivo.start()   
            self.inicio = 1

    def ACK(self,activ,client): 
        self.vec = activ
        if (len(self.vec)):                 #JFMB leemos la lista de activos
            for i in range(len(self.vec)):
                idee = str(self.vec[i]).encode()
                akc = b'\x05' + b'$' + idee
                client.publish('comandos/22/'+self.vec[i], akc)     #JFMB y publicamos a cada uno de ellos el ACK

    def recvaudio(self,client,receptores,emisor,tamaño):        #JFMB metood para recibir audio
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
                        
                        audior.close()
                        server_socket.close()
                        self.FRR(client,receptores,emisor,tamaño)
            audior.close()
            server_socket.close()
        
        au = threading.Thread(name = 'audio hilo', target = recibiraudio,daemon = True)
        #Luego de configurar cada hilo, se inicializan
        au.start() 

    def FRR(self,client,receptores,emisor,tamaño):      #JFMB luego de recibir audio nos manda al FRR
        emisr = str(emisor).encode()
        tam = str(tamaño).encode()
        FRR = b'\x02' + b'$' + emisr + b'$' + tam
        print('Esto son los receptores'+ str(receptores))
        for i in range(len(receptores)):
            client.publish('comandos/22/'+str(receptores[i]), FRR ) #JFMB le publicamos a todos los receptores el FRR
        self.enviarAu()

    def enviarAu(self):             #y nos vamos a enviar audio
        def envrau():
            server_socket = socket()
            #server_socket.bind((SERVER_ADDR, SERVER_PORT))
            server_socket.listen(0) #1 conexion activa y 9 en cola
            try:
                while True:
                    print("\nEsperando conexion remota...\n")
                    conn, addr = server_socket.accept()
                    print('Conexion establecida desde ', addr)
                    print('Enviando Audio...')
                    with open('recibido.wav', 'rb') as audio: #Se abre el archivo a enviar en BINARIO
                        conn.sendfile(audio, 0)
                        audio.close()
                    conn.close()
                    print("\n\nArchivo enviado a: ", addr)
            finally:
                print("Cerrando el servidor...")
                server_socket.close()      
        envau = threading.Thread(name = 'audio hilo enviar', target = envrau,daemon = True)
        #Luego de configurar cada hilo, se inicializan
        envau.start()  

class Servidor(Comandos):               #JFMB clase de servidor
    def __init__(self, subs, destino):
        self.subs = subs
        self.destino = destino

    def conecmqtt(self):                    #JFMB Metodo para conectar al broker
        qos =2
        inicio = 0
        client = mqtt.Client(clean_session=True)
        client.on_message = self.on_message
        client.username_pw_set(MQTT_USER, MQTT_PASS)
        client.connect(host = MQTT_HOST, port = MQTT_PORT)
        client.subscribe([("comandos/22/201742012", qos), ("comandos/22/201701026", qos), ("comandos/22/201709532", qos), ("comandos/22", qos)])
        self.recibir(client)

    def recibir(self,client):       #JFMB recibimos infinitamente mensajes por hilos
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