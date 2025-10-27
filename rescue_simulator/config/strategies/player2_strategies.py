import time  
from src.pathfinding import a_star, dijkstra_recurso_mas_cercano

class Estrategia:
    def __init__(self, jugador, base, tablero):
        self.jugador = jugador
        self.base = base
        self.tablero = tablero

    def ejecutar_estrategia(self):
        # Recorre los vehículos de la base
        for vehiculo in self.base.vehiculos:
            # Buscar el recurso más cercano disponible
            recurso_objetivo = dijkstra_recurso_mas_cercano(vehiculo, self.tablero)
            if recurso_objetivo is None:
                print(f"No hay recursos disponibles para el vehículo {vehiculo.tipo}")
                continue
            
            # Calcular camino con 
            camino = a_star(vehiculo, self.tablero, recurso_objetivo)
            
            # Mover vehículo paso a paso
            for pos in camino[1:]:  # Excluimos la posición inicial
                vehiculo.mover(pos)
                self.tablero.actualizar_matriz_parcial()
                #self.tablero.mostrar_tablero() ---LO COMENTO PORQUE NECESITO PROBARLO SIN ESTO
                time.sleep(0.2)  # Retardo para simular movimiento

            # Marcar recurso como recogido
            vehiculo.agarrar_recurso(self.tablero)
            if vehiculo.viajes_restantes <= 0:
            #    vehiculo.volver_a_la_base
                continue