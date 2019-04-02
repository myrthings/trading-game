'''
 ----------------------------------------
|    Juego LaBolsa creado por:           |
|    - Myriam Barnés Guevara             |
|    - Jessica Costoso Martín            |
|    - Juan Manuel Espinosa Rodríguez    |
|    - Eduardo Ortega Marazuela          |
|   Abril 2019                           |
 ----------------------------------------
'''
from multiprocessing.connection import Listener, AuthenticationError
from multiprocessing import Process, Manager, Lock
import paho.mqtt.publish as publish
from time import sleep
import random
from datetime import datetime

## CONSTANTES GLOBALES
Hinf = 00 #hora de apertura de la bolsa
Minf = 00
Hsup = 25 #hora de cierre de la bolsa
Msup = 30

broker = "172.16.16.128"
liste = "172.16.16.128" #listener-client

## FUNCIÓN PARA COMPROBAR SI LA BOLSA ESTÁ ABIERTA
def horacorrecta():
    fecha=datetime.now()
    H = int(fecha.strftime("%H"))
    M = int(fecha.strftime("%M"))
    if H>Hsup or H<Hinf:
        return False
    elif H==Hsup and M>=Msup:
        return False
    elif H==Hinf and M<Minf:
        return False
    else:
        return True

## FUNCIÓN QUE DEVUELVE EL RANKING
def ranking():
    ranking=[]                   
    for user in list(datos_usuarios.keys()):
        acum=0
        for empresa in list(datos_usuarios[user]['empresas'].keys()):
            acum+=info_empresas[empresa]['Precio']*datos_usuarios[user]['empresas'][empresa]
        acum+= datos_usuarios[user]['cash']
        ranking.append((user,acum)) 
    ranking.sort(key=lambda par:par[1],reverse=True)
    
    return ranking

## FUNCIÓN QUE COMPRUEBA SI UN USUARIO ESTÁ Y SI SU CONTRAS COINCIDE
def comprobar(user,pw,diccionario):
    if user in diccionario:
        if diccionario[user]==pw:
            return True
        else:
            return False
    else:
        return False

## FUNCIÓN DE RECOGIDA Y ENVÍO DE DATOS EN TIEMPO REAL
def publicar(empresas,infoempresas):
    from bs4 import BeautifulSoup #libreri­a para scrapear webs
    from urllib.request import urlopen #para poder meter urls
    
    fecha=datetime.now()
    print('Se abre la bolsa', fecha.strftime("%d-%m-%Y %H:%M"))
    url = 'http://www.bolsamadrid.es/esp/aspx/Mercados/Precios.aspx?indice=ESI100000000&punto=indice' 
    
    j=0
    while True:
        if horacorrecta():
            content = urlopen(url).read()
            soup = BeautifulSoup(content)
            acciones = soup.find(id="ctl00_Contenido_tblAcciones")
            
            fecha=datetime.now()
            print('Actualización...', fecha.strftime("%H:%M"))
            for item in acciones.find_all('tr'): #por cada fila
                i=0 
                for piece in item.find_all('td'): #por cada elem de la fila
                    elem=piece.get_text()
                    if i==0:
                        company=elem.replace(' ','_') #eliminamos los espacios del nombre
                        if j==0:
                            empresas.append(company)
                            historial=[]
                            cambios=[]
                        else:
                            cambios=infoempresas[company]['Camb']
                            historial=infoempresas[company]['Hist'] #en el historial guardamos todos los precios
                    elif i==1: 
                        precio=float(elem.replace(',','.')) #actualizamos el precio
                        historial.append(precio)
                    elif i==2: 
                        var=float(elem.replace(',','.'))
                        cambios.append(var)
                        break #no seguimos mirando
                    i+=1
                if i>=1: #para evitar el primer item vacío
                    infoempresas[company]={'Precio':precio, 'Var':var, 'Hist':historial, 'Camb':cambios} #actualizamos el diccionario
                    if var>0:
                        var='+'+str(var)
                    print('Enviando...  '+'{:14}'.format(company)+'Precio: '+'{:<8}'.format(precio)+'Var: '+'{:<8}'.format(str(var)+'%'))
                    publish.single(company,'{:14}'.format(company)+ 'Precio: '+'{:<8}'.format(precio)+'Var: '+'{:<8}'.format(str(var)+'%'), hostname=broker) #enviamos a la red
            if j==0:
                j+=1
        else:
            print('La bolsa está cerrada')
        sleep(30)
    
## FUNCIÓN DE SIMULACIÓN DE LA BOLSA (por si no hay internet)
def publicarficticio(empresas,infoempresas):    
    print('Simulando bolsa ficticia...')
    #hacemos una primera inicialización de los datos
    for letter in ['BANANA','HIPPITEX','CELTDROLA','MACROHARD','ZONAMA']: #creamos 5 empresas ficticias
        empresas.append(letter)
        precio=round(random.random()*10,3)
        historial=[]
        cambios=[]
        historial.append(precio)
        infoempresas[letter]={'Precio':precio,'Var':0, 'Hist':historial, 'Camb':cambios}
        
    while True:
        if horacorrecta():
            for company in ['BANANA','HIPPITEX','CELTDROLA','MACROHARD','ZONAMA']: #creamos 5 empresas ficticias
                nuevavar=round(random.random(),3)
                nuevoprecio=infoempresas[company]['Precio']+nuevavar/100 #de esta manera incrementa o decrementa el precio
                if nuevoprecio>0:
                    precio=nuevoprecio #para que no haya acciones negativas
                    var=nuevavar
                historial=infoempresas[company]['Hist']
                historial.append(precio)
                cambios=infoempresas[company]['Camb']
                cambios.append(var)
                infoempresas[company]={'Precio':precio,'Var':var, 'Hist':historial, 'Camb':cambios} #actualizamos el diccionario
                print('Enviando...  '+'{:14}'.format(company)+'Precio: '+'{:<8}'.format(precio)+'Var: '+'{:<8}'.format(str(var)+'%'))
                publish.single(company, '   Precio: '+'{:<8}'.format(precio)+'Var: '+'{:<8}'.format(str(var)+'%'), hostname=broker) #enviamos a la red
        else:
            print('La bolsa está cerrada')
        sleep(60)

    
## FUNCIÓN QUE INTERACTÚA CON EL CLIENTE Y AUXILIAR SEGÚN EL PROTOCOLO 
def mensajeria(conn,id,usuarios,datos_usuarios,lock,lista_empresas,info_empresas):
    try:
        
        if not(horacorrecta()):
            conn.send("Hora limite")
            conn.send(str(ranking()))
        else:
            conn.send("Hora correcta")
            
            ## MENU DE REGISTRO
            conn.send('1. Acceder  2. Registrse') #envía el menú
            respuesta = conn.recv() #recibe la opción
            
            if respuesta=='1':    
                user = conn.recv() #recibe el usuario
                passw = conn.recv() #recibe la contrasena
                b = comprobar(user,passw,usuarios) #comprueba que exista en la base de datos
            
            elif respuesta == '2':
                while True:
                    user = conn.recv() #recibe el usuario
                    passw = conn.recv() #recibe la contrasena
                    if (user in usuarios) or (user in lista_empresas):
                        conn.send('Usuario ya existente') #envía si es correcto o no
                    else:
                        conn.send('Usuario correcto')
                        break
                
                ## crea el nuevo usuario
                lock.acquire()
                usuarios[user]=passw
                datos_usuarios[user]={'cash':100000,'empresas':{}}
                lock.release()
                
                print('Usuario nuevo creado',datos_usuarios)
                b = True
    
            else:
                b = False 
            
            if b: #si se ha hecho bien el proceso seguimos
                conn.send('ok')
                conn.send(str(lista_empresas)) #enviamos la lista de empresas
                print ("You are welcome")
                
                ## MENU DE ACCIONES
                while True:
                    respuesta = conn.recv() #recibe la opción del menu
                    if not(horacorrecta()):
                        conn.send("Hora limite")
                        conn.send(str(ranking()))
                        publish.single(user, 'cerrar', hostname=broker)
                        break
                    else:
                        conn.send("Hora correcta")
                    ## COMPRAR
                    if respuesta == '1':
                        empresa = conn.recv() #recibe el nombre de la empresa
                        if empresa!='s':
                            try:
                                numero_acc = int(conn.recv()) #recibe el número de acciones
                                #hace la compra
                                lock.acquire()
                                actualizaDiccionarioComprar(empresa,numero_acc,datos_usuarios,user,info_empresas)
                                lock.release()
                            except:
                                conn.send('No es un numero') #salimos al menú principal
                    
                    ## VENDER
                    elif respuesta == '2':
                        while True:
                            empresa = conn.recv() #recibe el nombre de la empresa
                            if empresa in datos_usuarios[user]['empresas']: #si el usuario la tiene
                                conn.send('ok')
                                try:
                                    numero_acc = int(conn.recv()) #recibe el número de acciones
                                    #hace la venta
                                    lock.acquire()
                                    actualizaDiccionarioVender(empresa,numero_acc,datos_usuarios,user,info_empresas)
                                    lock.release()
                                except:
                                    conn.send('No es un numero')
                                break
                            elif datos_usuarios[user]['empresas']=={}:
                                conn.send('No tienes empresas')
                                break
                            elif empresa=='s':
                                break
                            else:
                                conn.send('No tienes acciones en esa empresa, elige otra (s para salir)')                       
                    
                    ## CONSULTAR LOS DATOS
                    elif respuesta== '3':
                        conn.send(str(datos_usuarios[user]))
                        conn.send(str(info_empresas))
                    
                    ## VER EMPRESAS
                    elif respuesta == '4':
                        conn.send(str(info_empresas))
                        respuesta= conn.recv()
                        if respuesta == '1':
                            conn.send("A que empresa te quieres suscribir: ")
                            while True:
                                empresa=conn.recv()
                                if empresa in lista_empresas:
                                    conn.send('ok')
                                    publish.single(user, 'S'+empresa, hostname=broker)
                                    conn.send('Suscrito a '+empresa+' con éxito')
                                    break
                                elif empresa=='s':
                                    conn.send('no')
                                    break
                                else:
                                    conn.send("Esa empresa no existe, elige otra (s para salir)")
                            
                        elif respuesta == '2':                            
                            conn.send("De que empresa te quieres desuscribir: ")
                            while True:
                                empresa=conn.recv()
                                if empresa in lista_empresas:
                                    conn.send('ok')
                                    publish.single(user, 'D'+empresa, hostname=broker)
                                    conn.send('Desuscrito de '+empresa+' con éxito')
                                    break
                                elif empresa=='s':
                                    conn.send('no')
                                    break
                                else:
                                    conn.send("Esa empresa no existe, elige otra (s para salir)")
                    
                    ## VER RANKING
                    elif respuesta=='5':
                        conn.send(str(ranking()))
                    
                    ## SALIR   
                    elif respuesta=='6':
                        conn.send('Adios')
                        publish.single(user, 'cerrar', hostname=broker)
                        break
                    
                    ## CUALQUIER OTRA COSA
                    else:
                        conn.send('Opcion no valida')
            else:
                conn.send('Nope')
                print('Usuario incorrecto')
    
    except EOFError:
        print('Usuario desconectado de manera abrupta')
    except ConnectionResetError:
        print('Usuario desconectado de manera abrupta')


## FUNCIÓN PARA COMPRAR LAS ACCIONES
def actualizaDiccionarioComprar(empresa,numero_acc,diccionario2,r,info_empresas):
    if numero_acc>0:
        if diccionario2[r]['cash'] >= numero_acc*info_empresas[empresa]['Precio']:
            dinero=(diccionario2[r]['cash'] - numero_acc*info_empresas[empresa]['Precio'])
            if empresa in diccionario2[r]['empresas']:
                acc=diccionario2[r]['empresas'][empresa]+ numero_acc
            else:
                acc= numero_acc
            dic_empresas=diccionario2[r]['empresas']
            dic_empresas[empresa]=acc
            diccionario2[r]={'cash':dinero,'empresas':dic_empresas}
            conn.send('Transaccion completada')
        else:
            conn.send('Dinero insuficiente')
    elif numero_acc<0:
        conn.send('No puedes comprar un numero de acciones negativas')

## FUNCIÓN PARA VENDER LAS ACCIONES
def actualizaDiccionarioVender(empresa,numero_acc,diccionario2,r,info_empresas):
    if numero_acc>0:
        dic_empresas = diccionario2[r]['empresas']
        if diccionario2[r]['empresas'][empresa] > numero_acc:
            dinero=diccionario2[r]['cash'] + numero_acc*info_empresas[empresa]['Precio']
            acc = diccionario2[r]['empresas'][empresa] -  numero_acc
            dic_empresas[empresa]=acc
            conn.send('Transaccion completada')
        elif diccionario2[r]['empresas'][empresa] < numero_acc: 
            conn.send('No dispone de suficientes acciones de la empresa')
            dinero = diccionario2[r]['cash']
        else: 
            del dic_empresas[empresa]
            dinero = diccionario2[r]['cash'] + numero_acc*info_empresas[empresa]['Precio']
            conn.send('Transaccion completada')
        diccionario2[r]={'cash':dinero,'empresas':dic_empresas}
    elif numero_acc<0:
        conn.send('No puedes vender un numero de acciones negativas')



if __name__ == '__main__':
    listener = Listener(address=(liste, 6001), authkey=b'secret password')
    print ('listener starting')
    
    manager = Manager()
    usuarios = manager.dict() #diccionario de usuarios y contraseñas
    datos_usuarios = manager.dict() #diccionario de usuarios con sus datos
    
    lock = Lock()
    
    lista_empresas = manager.list() #lista con las empresas que existen
    info_empresas = manager.dict() #diccionario con las empresas, precio y volumen (datos nec para las acciones)
    
    # por si no hay conexión a internet poder usarlo
    internet = input('Conexión a internet? s/n: ')
    if internet=='s':
        q = Process(target=publicar, args=(lista_empresas,info_empresas))
        q.start()
    else: ## por si no tenemos internet o beautiful soup simulamos una bolsa
        q = Process(target=publicarficticio, args=(lista_empresas,info_empresas))
        q.start()
        
    
    # controlador de las conexiones
    while True:
        print ('accepting conexions')
        try:
            conn = listener.accept()                
            print ('connection accepted from', listener.last_accepted)
            p = Process(target=mensajeria, args=(conn,listener.last_accepted,usuarios,datos_usuarios,lock,lista_empresas,info_empresas))
            p.start()
        except AuthenticationError:
            print ('Connection refused, incorrect password')
            

    listener.close()
    



































