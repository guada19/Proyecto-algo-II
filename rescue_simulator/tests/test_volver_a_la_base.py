import sys
import os

# Añade el directorio principal (../) al PYTHONPATH.
# Esto permite importar módulos como 'src.map_manager'.
#Basicamente le dice al archivo que debe buscar los módulos por fuera de la carpeta test y que busque en toda la carpeta de rescue_simulator
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.map_manager import Tablero
from src.aircraft import Jeep
from src.resources import Resource

# 1. Crear tablero y un vehículo de J1
tablero = Tablero(ancho=12, largo=10)
v = Jeep(posicion=(5, 5), jugador="J1")

# 2. Crear carga de prueba
r1 = Resource((0, 0), 10, "disponible", "mercancia")
r1.subtipo = "ropa"
v.carga_actual.append(r1)

# 3. Registrar el vehículo en el tablero
tablero.vehiculos.append(v)

# 4. Simular que se mueve hacia su base
print(f"Posición inicial: {v.posicion}")
while v.y > 0:
    v.volver_a_la_base(tablero)
    print(f"Vehículo en {v.posicion}")

print("Puntajes:", tablero.puntaje)
print("Carga actual:", v.carga_actual)
