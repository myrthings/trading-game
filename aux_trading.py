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
from paho.mqtt.client import Client
from tkinter import Tk, Listbox, font, Scrollbar
import sys

## CONSTANTES GLOBALES
broker = "172.16.16.128"
canalPersonal = str(sys.argv[1])

def on_message(client, userdata, msg):
    if msg.topic == canalPersonal: # Los msg que llegan por el canal personal sirven para las acciones auxiliares
        if str(msg.payload.decode("utf-8"))[0]== 'S':
            client.subscribe(str(msg.payload.decode("utf-8"))[1:]) # Suscribir
        elif str(msg.payload.decode("utf-8"))[0]== 'D':
            client.unsubscribe(str(msg.payload.decode("utf-8"))[1:]) # Desuscribir
        elif str(msg.payload.decode("utf-8"))=='cerrar': # Fin del programa
            window.destroy() # Cerrar ventana
            client.close() # Cerrar cliente
    else:
        listb.insert('end',str(msg.payload.decode("utf-8"))) # Los msg que llegan por el canal de las empresas se añaden a la pantalla
        listb.pack()

## ENTORNO GRÁFICO
window=Tk()
window.geometry("540x340+350+70")
window.title("Empresas suscritas")

scrollbar=Scrollbar(window,orient='vertical')
listb=Listbox(window,width=720,height=1200,borderwidth=0,font=font.Font(family='ClearType',size=14),yscrollcommand=scrollbar.set)
scrollbar.config(command=listb.yview)
scrollbar.pack(side='right',fill='y')


if __name__=="__main__":

    client = Client()
    client.on_message = on_message

    client.connect(broker)
    
    client.subscribe(canalPersonal) # canal de comunicación con el servidor
    client.loop_start() # inicio de las comunicaciones
    
    window.mainloop() # funcionamiento de la ventana
    
        