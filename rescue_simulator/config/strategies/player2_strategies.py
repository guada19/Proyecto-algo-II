from src.pathfinding import a_star, dijkstra_recurso_mas_cercano

class Estrategia_J2:
    def __init__(self, jugador, base, tablero):
        self.jugador = jugador
        self.base = base
        self.tablero = tablero
        
    def obtener_siguiente_paso(self, vehiculo):
        
        if len(vehiculo.carga_actual) == vehiculo.capacidad_carga or vehiculo.viajes_restantes <= 0:
            objetivo = self.base.posicion 
            
            if vehiculo.posicion == objetivo:
                return None
            else:
                return (vehiculo.x, objetivo)
        
        else:
            
            if vehiculo.camino_restante and not self.recurso_en_camino_es_valido(vehiculo):
                vehiculo.camino_restante = [] 
            
            if not vehiculo.camino_restante:
                
                recurso_objetivo = dijkstra_recurso_mas_cercano(vehiculo, self.tablero) 
                
                if recurso_objetivo is None:
                    return None
                
                camino = a_star(vehiculo, self.tablero, recurso_objetivo)
                
                vehiculo.camino_restante = camino[1:]
                
        if vehiculo.camino_restante:
            
            return vehiculo.camino_restante.pop(0) 
        
        return None 

    def recurso_en_camino_es_valido(self, vehiculo):
        """
        Verifica si el recurso al final del camino planificado sigue disponible en el tablero.
        """
        if not vehiculo.camino_restante:
            return False
            
        destino = vehiculo.camino_restante[-1]
        
        recurso = self.tablero.pos_recursos.get(destino)
        
        return recurso is not None and recurso.estado == "disponible" and recurso.categoria in vehiculo.tipo_carga_permitida

"""
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
                self.tablero.mostrar_tablero()
                time.sleep(0.2)  # Retardo para simular movimiento

            # Marcar recurso como recogido
            vehiculo.agarrar_recurso(self.tablero)
            if vehiculo.viajes_restantes <= 0:
            #    vehiculo.volver_a_la_base
                continue


"""
