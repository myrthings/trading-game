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
from multiprocessing.connection import Client
from ast import literal_eval #para poder pasar de str a otro tipo
import subprocess
import matplotlib.pyplot as plt

## CONSTANTES GLOBALES
broker = "172.16.16.128"
liste = "172.16.16.128"

aux = 'aux_trading.py' #ubicación del archivo aux_LaBolsa.py

## FUNCIÓN QUE INTERACTÚA CON EL SERVIDOR
def menu(conn):
    hora=conn.recv()
    if hora=="Hora correcta":
        print(conn.recv()) #recibe el menú
        m = input() #entra la opción por pantalla
        conn.send(m) #envía la opción al servidor
        
        ## MENU DE USUARIO
        if m=='1': 
            user = input('Usuario: ') #pide el nombre de usuario
            conn.send(user) #envia el nombre de usuario
            passw = input('Contrasena: ') #pide la contraseña
            conn.send(passw) #envía la contraseña
        
        elif m=='2':
            while True:
                user = input('Nuevo usuario: ') #pide el usuario
                conn.send(user) #envia el usuario
                passw = input('Contrasena: ') #se introduce la contrasena
                conn.send(passw) #envía la contrasena
                respuesta=conn.recv() #recibe si es correcto o no el usuario
                if respuesta == 'Usuario correcto':
                    print(respuesta)
                    break
                else:
                    print("Ese nombre no está permitido")
        
        else:
            print('Esa opción no existe')
        
        c = conn.recv() #recibe 'ok' si se ha hecho bien la lectura de usuarios
        
        if c == 'ok':
            subprocess.Popen(['python3',aux,user]) #abre el archivo auxiliar
            lista_empresas=eval(conn.recv()) #recibe la lista de empresas
            print('Empresas abiertas hoy:')
            i=0
            while i<len(lista_empresas):
                print('{:14}'.format(lista_empresas[i])+'{:14}'.format(lista_empresas[i+1])+'{:14}'.format(lista_empresas[i+2])+'{:14}'.format(lista_empresas[i+3])+'{:14}'.format(lista_empresas[i+4]))
                i+=5
            while True:
                print('\n'+'Que te interesa hacer?')
                menu = input('1. Comprar'+'\n'+'2. Vender'+'\n'+'3. Consultar tus datos'+'\n'+'4. Informacion de empresas y subscripciones'+'\n'+'5. Ver ranking'+'\n'+'6. Salir'+'\n'+'Opción: ')
                conn.send(menu) #envía la opción del menú
                hora=conn.recv()
                if hora == "Hora limite":
                    print("La bolsa ha cerrado")
                    ranking= literal_eval(conn.recv())
                    i=1
                    for j in ranking:
                        if i>10:
                            break
                        print(str(i)+' '+'{:10}'.format(j[0])+' -----> ' +'{:10}'.format(round(j[1],3))+'€')
                        i+=1
                    break
                
                ## MENU DE ACCIONES
        
                ## COMPRAR
                if menu=='1':
                    while True:
                        emp = input('En que empresa quieres comprar?: ') #entra el nombre de la empresa
                        if emp in lista_empresas: #si existe
                            conn.send(emp) #la envía
                            acc = input('Cuantas acciones quieres comprar?: ')
                            conn.send(acc) #envía el número de acciones
                            print(conn.recv())
                            break #y salimos
                        elif emp=='s':
                            conn.send(emp)
                            break
                        else: #si no existe la vuelve a pedir
                            print('La empresa',emp,'no existe, elige otra (s para salir):')
        
                ## VENDER
                elif menu=='2':
                    while True:
                        emp = input('En que empresa quieres vender?: ')
                        conn.send(emp)
                        if emp=='s': #s es para salir
                            break
                        else:
                            mess=conn.recv()
                            if mess=='ok':
                                acc = input('Cuantas acciones quieres vender?: ')
                                conn.send(acc)
                                print(conn.recv())
                                break
                            elif mess=='No tienes empresas':
                                print(mess)
                                break
                            else:
                                print(mess)

        
                ## INFORMACION DEL USUARIO
                elif menu=='3':
                    info=conn.recv()
                    info_empresas=conn.recv()
                    dic=literal_eval(info)
                    dic2=literal_eval(info_empresas)
                    print('---------------------------------------')
                    print('{:20}'.format('Datos del usuario:')+user)
                    print('\n'+'{:20}'.format('Saldo disponible:')+str(dic['cash']))
                    print('\n'+'Empresas:')
                    acum=0
                    for empresa in dic['empresas']:
                        t=round(dic2[empresa]['Precio']*dic['empresas'][empresa],3)
                        print('{:15}'.format(empresa)+'Acciones: '+'{:10}'.format(str(dic['empresas'][empresa]))+'Valor: '+'{:10}'.format(str(t)+'€'))
                        acum+=dic2[empresa]['Precio']*dic['empresas'][empresa]
                    print('\n'+'Dinero total invertido: '+str(round(acum,3))+'€')
                    print('---------------------------------------')
                
                ## VER EMPRESAS Y SUSCRIPCIONES
                elif menu=='4':
                    lista=literal_eval(conn.recv())
                    for empresa in list(lista.keys()):
                        var=lista[empresa]['Var']
                        if var>=0:
                            var='+'+str(var)
                        else:
                            var=str(var)
                        print('{:14}'.format(empresa)+"Precio: "+'{:<8}'.format(lista[empresa]['Precio'])+'Var: '+'{:<6}'.format(var+'%'))
                    respuesta=input('\n'+'1. Suscribir' +'\n'+ '2. Desuscribir'+'\n'+ '3. Graficas'+'\n'+'4. Volver al menu'+'\n'+'Opcion: ')
                    conn.send(respuesta)
                    ## SUSCRIBIRSE
                    if respuesta == '1':
                        print(conn.recv())
                        while True:
                            empres = input()
                            conn.send(empres)
                            res=conn.recv()
                            if res=='ok':
                                print(conn.recv())
                                break
                            elif empres=='s':
                                break
                            else:
                                print(res)
                    ## DESUSCRIBIRSE        
                    elif respuesta == '2':
                        print(conn.recv())
                        while True:
                            empres = input()
                            conn.send(empres)
                            res=conn.recv()
                            if res=='ok':
                                print(conn.recv())
                                break
                            elif empres=='s':
                                break
                            else:
                                print(res)
                    
                    elif respuesta == '3':
                        emp=input('Que empresa quieres visualizar? (c para comparar): ')
                        if emp in lista_empresas:
                            historial=lista[emp]['Hist']
                            if len(historial)<10:
                                print('No hay suficientes datos')
                            else:
                                plt.plot([i for i in range(len(historial))],historial,'r')
                                plt.ylabel(emp)
                                plt.title("Valor de "+emp+" a lo largo del día de hoy")
                                plt.show()
                        elif emp=='c':
                            listo=input('Introduce las empresas que quieres comparar separadas por un espacio: ')
                            listo=listo.split()
                            b=False
                            for emp in listo:
                                if emp in lista_empresas:
                                    b=True
                                    cambios=lista[emp]['Camb']
                                    if len(cambios)<0:
                                        print('No hay suficientes datos')
                                        break
                                    plt.plot([i for i in range(len(cambios))],cambios,label=emp)
                                else:
                                    print("Empresa "+emp+" no válida")
                            if b: #para comprobar que al menos pintemos una empresa
                                plt.plot([i for i in range(len(cambios))],[0 for i in range(len(cambios))],'k',linewidth=1,linestyle='--')
                                plt.title("Comparativa de empresas")
                                plt.legend()
                                plt.show()
                                    
                        else:
                            print("Empresa no disponible")
                
                ## VER RANKING
                elif menu=='5':           
                    ranking= literal_eval(conn.recv())
                    i=1
                    for j in ranking:
                        if i>10:
                            break
                        print(str(i)+' '+'{:10}'.format(j[0])+' -----> ' +'{:10}'.format(round(j[1],3))+'€')
                        i+=1
                ## SALIR    
                elif menu=='6': 
                    print(conn.recv())
                    break
                
                ## OTRA COSA
                else:
                    print(conn.recv())
        
        else: #si no es ok salimos
            print('Error de usuario')
    else:
        print("Bolsa cerrada")
        ranking=literal_eval(conn.recv())
        i=1
        for j in ranking:
            if i>10:
                break
            print(str(i)+' '+'{:10}'.format(j[0])+' -----> ' +'{:10}'.format(round(j[1],3))+'€')
            i+=1
 
       
if __name__ == '__main__':
    print ('trying to connect')
    conn = Client(address=(liste, 6001), authkey=b'secret password')
    print ('connection accepted')
    
    menu(conn) # comunicacion




