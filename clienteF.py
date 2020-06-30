#Jose Fernando Marticorena Barrientos  201701026
#Jonathan Mardoqueo Lorenzo Lopez

import paho.mqtt.client as mqtt     #libreria cliente Mqtt
import logging                      #Para mostrar informacoin
import time                         
import os                           
import logging
import datetime                     #Para generar fecha/hora actual
import binascii
import threading                    #Concurrencia con hilos
from socket import socket
from broker import *                #Informacion de la conexion
from socket import SHUT_RDWR
from  string import ascii_lowercase, ascii_uppercase #JMLL Para encriptar el testo

servi = '167.71.243.238'           #JMLL constantes para conexion por TCP
SERVER_ADDR = ''
SERVER_PORT = 9822
BUFFER_SIZE = 64 * 1024
CMD_ID = 'comandos/22/201701026'
cont=0


class Comandos:                         #JFMB Creacion de clase comandos 
    def __init__(self, comando):        #JFMB definimos los objetos
        self.comando = comando
        #self.detectar(l1)

    def ftr(self,destino,tamaño,client,id):       #JFMB metodo para comando FTR se manda a llamar en Cliente
        destin = str(destino).encode()
        tam = str(tamaño).encode()
        comando =  'comandos/22/'+str(id)      
        FTR = b'\x03' + b'$' + destin + b'$' + tam      #JFMB se adjunta la trama en binario con el codigo de FTR
        client.publish(comando, FTR)                     #JFMB Se publica la trama  


class Cliente(Comandos):                            #JFMB Funcion cliente oriantada a comandos
    def __init__(self, subs, destino):
        self.subs = subs
        self.destino = destino
        
    def conecmqtt(self):                            #JFMB metodo para realiar la conexion al mqtt
        client = mqtt.Client(clean_session=True)   #JFMB cliente como una nueva secion limpia
        client.on_message = self.on_message             #JFMB On message la funcion al recibir un msg
        client.username_pw_set(MQTT_USER, MQTT_PASS)
        client.connect(host = MQTT_HOST, port = MQTT_PORT)  #JFMB conexion al broker
        self.subscribir(client)                             #JFMB LLmamamos al metdo de subscripcion

    def subscribir(self,client):                     # Metodo para subcrcibir a todos los topicos
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
        client.subscribe("comandos/22/"+ self.id)

#JFMB Hilo para recibir mensajes todo el tiempo, con delay al loop start para que reciba en ese tiempo

        def recibir():
            while True:
                client.loop_start()  
                time.sleep(1) 

        t1 = threading.Thread(name = 'recibir', target = recibir,daemon = True)
        t1.start()

#JFMB Hilo para enviar ALIVES con el codigo x04 en comandos/22 y publicarlo directo al servidor
        ide = str(self.id).encode()
        Ali = b'\x04' + ide
        def ALIVE():
            while True:
                client.publish('comandos/22', Ali)
                #print("contadpor : "+ str(i))
                time.sleep(2) #Delay en segundos

        alive = threading.Thread(name = 'ACtivo', target = ALIVE, daemon = True)
        #Luego de configurar cada hilo, se inicializan
        alive.start()

#  JFMB LLamamos al metodo menu
        self.menu(client)
        
    def menu(self,client):          #JFMB En menu basicamente mostramos la interfaz para el usuario
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
                    self.enviartxt(client,destino)          #JFMB LLamamos al metodo que Codifica el Texto y luego lo envia

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
                    self.enviartxt(client,destino)     #JFMB LLamamos al metodo que Codifica el Texto y luego lo envia


            if(self.menu1 == '2'):                     #JFMB Menu para enviar mensajes de audio
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
                    destino =  destino 
                    self.menu3 = '1'
                    duracion = input('------Ingrese la duracion del audio(Seg.): ')  #Basicamente solo pedimos el destino y la duracion
                    self.grabarAu(duracion,destino,client)        #llamamos al metodo que graba

            #el mismo procedimiento para las salas
                if(self.menu2 == '2'):
                    print("------A SALA------")
                    while n !=1:
                        destino = input("Ingrese la sala: Ej.('22S01'): ")
                        if(len(destino) != 5):
                            print("Sala invalida!!! Vuelva a ingresar")
                            n =0
                        else:
                            n =1
                    destino = destino
                    self.menu3 = '1'
                    duracion = input('------Ingrese la duracion del audio(Seg.): ')
                    self.grabarAu(duracion,destino,client)

            if(self.menu1 =='3'):  #JFMB si escogemos la opcion3 sale del programa
                exit()

    def enviartxt(self, client, destino):   #JMLL Metodo para enviar texto
        msm = input("escribe y manda...")   #JMLL Ingresamos el texto

        def Encriptacion(texto, pasos):     #JMLL funcion para encriptar texto
            resultado = []                  #JMLL se crea una lista vacia para guradar el resultado

            for i in texto:                 #JMLL se itera por cada caracter del texto original
                if i in ascii_lowercase:    #JMLL Se verifica si se esta en las minusculas
                    indice = ascii_lowercase.index(i)    #JMLL se calcula el indice en donde se encuentra el caracter
                    nuevo_indice = (indice + pasos) % len(ascii_lowercase) #JMLL se calcula nuevo indice para hacer la rotacion y se le suman los pasos.
                    resultado.append(ascii_lowercase[nuevo_indice])  #JMLL se agrega el nuevo caracter en la lista
                elif i in ascii_uppercase:  #JMLL se verfica si se esta en las mayusculas
                    indice = ascii_uppercase.index(i)    #JMLL se calcula el indice en donde se encuentra el caracter
                    nuevo_indice = (indice + pasos) % len(ascii_uppercase) #JMLL se calcula el nuevo indice para hacer la rotacion y se le suman os pasos
                    resultado.append(ascii_uppercase[nuevo_indice]) # JMLL Se agrega el nuevo caracter en la lista
                else:
                    resultado.append(i)     #JMLL si no encuentra mayusculas o minusculas, se agrega a resultado  ese caracter

            return ''.join(resultado)       #JMLL se cambia el resultado de lista a una cadena de caracteres.
        msm = Encriptacion(msm, 3500)       #JMLL Se llama la funcion de encriptacion para codificar el mensaje que se enviara.
        client.publish(destino, msm)       #JMLL publicamos la info al destino
        print("-------Enviado--------- ")   #JMLL se imprime en patalla que se a enviado el mensaje.
    
    def grabarAu(self,duracion,destino,client):     #JMLL Se define el metodo para grabar el audio
        logging.basicConfig(level = logging.DEBUG, format = '%(message)s')   #JMLL se muestra el mensaje
        logging.info('Comenzando grabacion')    #JMLL se despliega el mensaje de que comenzo la grabacion
        os.system('arecord -d '+str(duracion)+ ' -f U8 -r 8000 enviado.wav')   #JMLL Se elijen los parametros y caracteristicas que tendra la grabacion
        logging.info('Grabacion finalizada, inicia reproduccion')    #JMLL   Se muestra en patalla que finalizo la grabacion
        os.system('aplay enviado.wav')      #JMLL  Se reproduce el audio recien grabado
        tamaño = os.stat('enviado.wav').st_size    #JMLL Se obtiene el tamaño del audio, que servira para poder recibirlo sin problemas.
        self.ftr(destino,tamaño,client,self.id)     #JMLL Sen envia el tamaño del audio

    def enviaraudio(self):   #JMLL metodo para enviar el audio
        sock = socket()      
        sock.connect((SERVER_ADDR, SERVER_PORT))   #Se conecta al servidor y al puerto
        while True:
            print("Enviando Audio...")     #JMLL se imprime en patalla 
            audio = open('enviado.wav', 'rb')   #JMLL se abre el archivo de audio grabado para enviarlo
            archivo = audio.read(64*1024)     
            while archivo:
                sock.send(archivo)              #JMLL se envia el audio por medio de socket
                archivo = audio.read(64*1024)
            break
        try:
            sock.send(chr(1))
        except TypeError:                       #JMLL se levanta una excepcion si ocurre un error en el envio del audio
            sock.send(bytes(chr(1), "utf-8"))
        sock.shutdown(SHUT_RDWR)
        audio.close()                           #JMLL se cierra el archivo de audio, para no tener errores en el envio
        sock.close()                            #JMLL se cierro el socket
        print("Archivo Enviado")                #JMLL se imprime que se envio el audio
        print("Cerrando el servidor...")        #JMLL se imprime que se cierra el servidor

#JMLL Hilo para recibir audio
    def recibirAu(self):                        #JMLLL Se define el metodo para recibir el audio
        def recibiraudio():                     
            sock = socket()                     
            sock.connect((servi, SERVER_PORT))  #JMLLL Se conecta al servidor y al puerto especifico 
            try:
                buff = sock.recv(BUFFER_SIZE)   #JMLLL  Se recibe el audio por medio de socket
                archivo = open('recibido.wav', 'wb') #JMLL Aca se guarda el archivo entrante
                while buff:
                    archivo.write(buff)             
                    buff = sock.recv(BUFFER_SIZE) #JMLL Los bloques se van agregando al archivo

                archivo.close() #JMLL Se cierra el archivo
                print("Recepcion de archivo finalizada") #JMLL se muestra, que el archivo se recibio 

            finally:
                print('Conexion al servidor finalizada')  #JMLL se imprime, que se cierra la conexion
                sock.close() #JMLL Se cierra el socket

        recau = threading.Thread(name = 'audio hilo recibir', target = recibiraudio,daemon = True)
        #Luego de configurar cada hilo, se inicializan
        recau.start()                 

    def Alivecontinuo(self, client,cont):
        def aliverapid(cont):
            c=0
            cont=1+cont
            while True:
                while c <= 4:
                    c = c+1
                    time.sleep(2)
                if(c==4 and cont<=1):
                    print('no conected')


        rapid = threading.Thread(name = 'audio hilo recibir', target = aliverapid(cont) ,daemon = True)
        #Luego de configurar cada hilo, se inicializan
        rapid.start() 


    def Desencriptacion(self, texto, pasos): #JMLL metodo para poder Desencriptar el mensaje que se recibe
        resultado = []                         #JMLL se crea una lista vacia para guardar el nuevo mensaje

        for i in texto:  #JMLL se itera por cada caracter del texto original
            if i in ascii_lowercase:            #JMLL Se verifica si se esta en las minusculas
                indice = ascii_lowercase.index(i)  #JMLL se calcula el indice en donde se encuentra el caracter
                nuevo_indice = (indice - pasos) % len(ascii_lowercase)  #JMLL se calcula nuevo indice para hacer la rotacion y se le restan los pasos.
                resultado.append(ascii_lowercase[nuevo_indice])   #JMLL se agrega el nuevo caracter en la lista
            elif i in ascii_uppercase:   #JMLL se verfica si se esta en las mayusculas
                indice = ascii_uppercase.index(i)   #JMLL se calcula el indice en donde se encuentra el caracter
                nuevo_indice = (indice - pasos) % len(ascii_uppercase)   #JMLL se calcula el nuevo indice para hacer la rotacion y se le restan los pasos
                resultado.append(ascii_uppercase[nuevo_indice])   # JMLL Se agrega el nuevo caracter en la lista
            else:
                resultado.append(i)    #JMLL si no encuentra mayusculas o minusculas, se agrega a resultado  ese caracter

        return ''.join(resultado)      #JMLL se cambia el resultado de lista a una cadena de caracteres.

    def on_message(self, client, userdata, msg): #JFMbmetodo de recibir los mensajes y mostrarlos
        comensaje = str(msg.payload)
        #Primero en la llegada de los Comandos Direccionar a la accion que debe tomar
        #JFMB Si llega x05 el ACK pass para no mostrar cada 6 seg que esta activo
        if( str(msg.topic) == 'comandos/22/'+self.id and (comensaje[3:6] == 'x05' or comensaje[3:6] == 'x03') ):
            #cont =1
            #self.Alivecontinuo(client,cont)
            pass 
        #JFMB si llega x06 el Ok en FTR empezar transmicion de Audio
        elif( str(msg.topic) == 'comandos/22/'+self.id and comensaje[3:6] == 'x06' ):
            #print('OK en FTR, Empezando transmision de Audio...') solo indicaba que empezaba a enviar el audio
            self.enviaraudio()
        #JFMB si llega x07 el NO, es porque el destinario no esta conectado
        elif( str(msg.topic) == 'comandos/22/'+self.id and comensaje[3:6] == 'x07' ):
            print('---------No estan activos los clientes..-------------')   
        #JFMB si llega x02 el FRR tenemos que activar TCP para recibir audio      
        elif( str(msg.topic) == 'comandos/22/'+self.id and comensaje[3:6] == 'x02' ):
            print('FRR Activas TPc para recepcion!!!!!...')
            time.sleep(3)
            self.recibirAu()
        else:
            #JFMB aca se leen los mensajes que no sean de comandos, solo usuarios o salas
            if (str(msg.topic)[:5] == 'salas' or str(msg.topic)[:7] == 'usuario'):
                c = self.Desencriptacion(str(msg.payload.decode("utf-8")),3500)
                print("\n --------NUEVO MENSJAE!----------")
                print(str(datetime.datetime.now().ctime()) + " " +str(msg.topic) + ": " + c)
                print("--------------------------------")
            #JFMB Todos los ifs de aca para abajo son configuracion para ver mejor el menu
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
            elif (self.menu1 == '2' and self.menu2 =='1' and self.menu3 == '1') :
                print("------MENSAJE DE AUDIO A USUARIO------")
                print("Escriba la duracion de grabacion en segundos:")                    
            elif (self.menu1 == '2' and self.menu2 =='2' and self.menu3 == '0') :
                print("------MENSAJE DE AUDIO A SALA------")
                print("Ingrese la sala: salas/22/S:")
            elif (self.menu1 == '1' and self.menu2 =='2' and self.menu3 == '1') :
                print("------MENSAJE DE AUDIO A SALA------")
                print("Escriba la duracion de grabacion en segundos:")                      


class Inicio(Cliente):      #JFMB Clase que da inicio al Cliente
    def __init__(self):
        self.conecmqtt()
Inicio() 
