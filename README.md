# README

### Requisitos del sistema:
**Lenguaje:**
 - python3
 
 **Bibliotecas específicas:**
 - multiprocessing
 - tkinter
 - paho-mqtt
 - beautifulsoup4
 - matplotlib

*Nota: beautifulsoup4 solo es necesaria en el servidor con conexión a internet*



### Instalación de los complementos específicos en linux o macox:
 `pip3 install --user biblioteca`
 


### Instrucciones de uso para el servidor:
1. Cambiar las constantes broker en `server_trading.py`.
2. Establecer la hora de apertura y cierre de la bolsa
3. Ejecutar el archivo del servidor
    - Si al marcar la opción de conexión a internet beautifulsoup da un un warning
      quitar o poner en la línea 39 del código el valor de features:
         `soup = BeautifulSoup(content,features="lxml")`
4. Hecho!



### Instrucciones para el jugador:
1. Cambiar las constantes del client en `client_trading.py` y en `aux_trading.py`.
2. Ejecutar el cliente
  - Si ocurren problemas:
     - Cambiar las constantes de broker y listener-client (si no estaban predeterminadas)
     - Cambiar el directorio del archivo auxiliar en la constante global aux
3. Jugar!

```
Creado por:
 - Myriam Barnés Guevara
 - Jessica Costoso Martín
 - Juan Manuel Espinosa Rodríguez
 - Eduardo Ortega Marazuela
```
