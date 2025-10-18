import sys
import os

# Añade el directorio principal (../) al PYTHONPATH.
# Esto permite importar módulos como 'src.map_manager'.
#Basicamente le dice al archivo que debe buscar los módulos por fuera de la carpeta test y que busque en toda la carpeta de rescue_simulator
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.map_manager import Tablero
from src.aircraft import Vehiculo
from src.resources import *


def test_entrega_puntaje():
    # 1. Crear tablero y vehículo
    tablero = Tablero(largo=10, ancho=12)
    v = Vehiculo(
        tipo="Jeep",
        posicion=(5, 1),
        capacidad_carga=3,
        viajes_restantes=10,
        tipo_carga_permitida=["persona", "mercancia"],
        estado="activo",
        jugador="J1",
        max_viajes=10
    )

    # 2. Crear recursos/personas
    alimento = Resource((0, 0), 10, "disponible", "mercancia")
    alimento.subtipo = "alimento"
    ropa = Resource((0, 0), 10, "disponible", "mercancia")
    ropa.subtipo = "ropa"
    persona = Person()
    persona.categoria = "persona"
    persona.tipo = "PER"

    # 3. Simular que el vehículo los recogió
    v.carga_actual = [alimento, ropa, persona]

    # 4. Poner al vehículo en la base izquierda (columna 0)
    v.x, v.y = 5, 0

    # 5. Ejecutar entrega
    tablero.registrar_entrega(v)

    # 6. Verificar resultados
    assert tablero.puntaje["J1"] > 0, "No se sumaron puntos"
    assert tablero.entregas["J1"] == 3, "No registró cantidad de entregas"
    assert len(v.carga_actual) == 0, "No vació la carga tras entregar"
