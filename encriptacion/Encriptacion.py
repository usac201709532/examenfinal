from  string import ascii_lowercase, ascii_uppercase

class enc(object):
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

    def Desencriptacion(texto, pasos):
        resultado = []

        for i in texto:
            if i in ascii_lowercase:
                indice = ascii_lowercase.index(i)
                nuevo_indice = (indice - pasos) % len(ascii_lowercase) 
                resultado.append(ascii_lowercase[nuevo_indice])
            elif i in ascii_uppercase:
                indice = ascii_uppercase.index(i)
                nuevo_indice = (indice - pasos) % len(ascii_uppercase) 
                resultado.append(ascii_uppercase[nuevo_indice])
            else:
                resultado.append(i)

        return ''.join(resultado)


if __name__ == "__main__":

    
    texto = "Ejemplo de encriptacion en python"
    a = enc.Encriptacion(texto, 1) #se hace la rotacion solo de un paso, por eso va el uno. Se puede cambiar y no importa 
    b=str(a)
    print(b)

    c = enc.Desencriptacion(b,1)
    d=str(c)
    print(d)