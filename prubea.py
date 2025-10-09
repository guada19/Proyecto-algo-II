from clase_vehiculo import *
from clase_tablero import *

ancho = 15
largo = 15

tablero = Tablero(ancho, largo)
tablero.inicializar_vehiculos(ancho)
tablero.mostrar_tablero()
tablero.ejecutar_turno_global()
print()
print()
print()
print()
tablero.mostrar_tablero()