from src.pathfinding import a_star, dijkstra_recurso_mas_cercano

class Estrategia_J2:
    def __init__(self, jugador, base, tablero):
        self.jugador = jugador
        self.base = base
        self.tablero = tablero
    
    def obtener_siguiente_paso(self, vehiculo):
        #Asignar estrategia solo si el estado del vehiculo es válido
        if getattr(vehiculo, "estado", "activo") != "activo":
            return None
        if getattr(vehiculo, "viajes_restantes", 0) <= 0:
            return None 

        #self._reactivar_si_puede(vehiculo)

        if not hasattr(vehiculo, "camino_restante"):   #Agregado para que funcione el regreso (creo)
            vehiculo.camino_restante = []        
        
        if not hasattr(vehiculo, 'objetivo_recurso'):
            vehiculo.objetivo_recurso = None

        if len(vehiculo.carga_actual) == vehiculo.capacidad_carga or vehiculo.viajes_restantes <= 0:
            #También tocado por la misma razón
            col_base = 0 if vehiculo.jugador in (1, "J1") else self.tablero.ancho - 1
            objetivo = (vehiculo.posicion[0], col_base)
            
            if vehiculo.posicion == objetivo:
                vehiculo.camino_restante = [] 
                return None
            
            if not vehiculo.camino_restante or vehiculo.camino_restante[-1] != objetivo:
                self.desasignar_recurso(vehiculo)
                camino = a_star(vehiculo, self.tablero, objetivo)
                vehiculo.camino_restante = camino[1:] if camino else []    #Toqueteado
            
            if vehiculo.camino_restante:
                next_pos = vehiculo.camino_restante[0]
                
                if self.tablero.colision_vehiculos_para_a_star(*next_pos) or self.tablero.colision_minas(*next_pos):
                    vehiculo.camino_restante = []
                    return None
                
        else:
            
            if self.tablero.step_count % 5 == 0:
                self.desasignar_recurso(vehiculo)
                vehiculo.camino_restante = []
                pass
            
            if not self.recurso_objetivo_valido(vehiculo):
                self.desasignar_recurso(vehiculo)
                vehiculo.objetivo_recurso = None
                vehiculo.camino_restante = []

            if vehiculo.objetivo_recurso is None:
                recurso_objetivo = dijkstra_recurso_mas_cercano(vehiculo, self.tablero)
                if recurso_objetivo is None:
                    return None
                vehiculo.objetivo_recurso = recurso_objetivo 

            objetivo = vehiculo.objetivo_recurso
            """
            if vehiculo.camino_restante:
                next_pos = vehiculo.camino_restante[0]
                
                if self.tablero.colision_vehiculos_para_a_star(*next_pos) or self.tablero.colision_minas(*next_pos):
                    #self.desasignar_recurso(vehiculo) 
                    #vehiculo.camino_restante = []
                    return None
            """

            if vehiculo.camino_restante:
                next_pos = vehiculo.camino_restante[0]

                if self.tablero.colision_vehiculos_para_a_star(*next_pos) or self.tablero.colision_minas(*next_pos):
                    #self.desasignar_recurso(vehiculo) 
                    vehiculo.camino_restante = []
                    return None

            if not vehiculo.camino_restante:
                camino = a_star(vehiculo, self.tablero, objetivo)

                if not camino or len(camino) < 2:

                    if vehiculo.objetivo_recurso is not None:
                         self.desasignar_recurso(vehiculo) 
                    return None

                vehiculo.camino_restante = camino[1:] if camino else []

        return vehiculo.camino_restante.pop(0) if vehiculo.camino_restante else None
        
    def desasignar_recurso(self, vehiculo):
        
        if hasattr(vehiculo, 'objetivo_recurso') and vehiculo.objetivo_recurso:
            recurso_pos = vehiculo.objetivo_recurso
            recurso = self.tablero.pos_recursos.get(recurso_pos)
            if recurso and recurso.asignado_a == vehiculo:
                recurso.asignado_a = None
        vehiculo.camino_restante = []
        vehiculo.objetivo_recurso = None

    def recurso_objetivo_valido(self, vehiculo):
        """
        Verifica si el recurso actual asignado al vehículo sigue siendo válido.
        """
        if vehiculo.objetivo_recurso is None:
            return False
    
        recurso = self.tablero.pos_recursos.get(vehiculo.objetivo_recurso)
        return (
            recurso is not None
            and recurso.estado == "disponible"
            and recurso.categoria in vehiculo.tipo_carga_permitida
            and recurso.asignado_a == vehiculo
        )

"""
    def _reactivar_si_puede(self, vehiculo):
        
        #Si el vehículo está en base, sin carga, con viajes disponibles y sin ruta/objetivo, elige un nuevo recurso y arma un camino para salir nuevamente.
        
        if getattr(vehiculo, "estado", "activo") != "activo":
            return
        if getattr(vehiculo, "viajes_restantes", 0) <= 0:
            return
        if getattr(vehiculo, "carga_actual", None):
            return
        if getattr(vehiculo, "camino_restante", None):
            if vehiculo.camino_restante:
                return
        if getattr(vehiculo, "objetivo_recurso", None):
            return

        origen = vehiculo.posicion

        # 1) Elegir recurso con Dijkstra
        objetivo = None
        try:
            objetivo = dijkstra_recurso_mas_cercano(vehiculo, self.tablero)
        except TypeError:
            try:
                objetivo = dijkstra_recurso_mas_cercano(vehiculo, self.tablero, self.jugador)
            except TypeError:
                objetivo = dijkstra_recurso_mas_cercano(vehiculo, self.tablero)

        if not objetivo:
            return

        vehiculo.objetivo_recurso = objetivo

        # 2) Caminar con A* hacia el objetivo (evitando minas/vehículos)
        path = []
        try:
            path = a_star(vehiculo, self.tablero, objetivo)
        except TypeError:
            # por si tu a_star requiere flags/kwargs; dejalo simple si no hace falta
            path = a_star(vehiculo, self.tablero, objetivo)

        vehiculo.camino_restante = path or []

"""




"""
    def ejecutar_estrategia(self):
        # Recorre los vehículos de la base
        for vehiculo in self.base.vehiculos:
@@ -30,4 +73,7 @@ def ejecutar_estrategia(self):
            vehiculo.agarrar_recurso(self.tablero)
            if vehiculo.viajes_restantes <= 0:
            #    vehiculo.volver_a_la_base
                continue
                continue


    def recurso_en_camino_es_valido(self, vehiculo):
        
        #Verifica si el recurso al final del camino planificado sigue disponible en el tablero.
        
        if not vehiculo.camino_restante:
            return False
            
        destino = vehiculo.camino_restante[-1]
        
        recurso = self.tablero.pos_recursos.get(destino)
        
        return recurso is not None and recurso.estado == "disponible" and recurso.categoria in vehiculo.tipo_carga_permitida

    
    def recurso_en_camino_es_valido(self, vehiculo):
        
        #Verifica si el recurso al final del camino planificado sigue disponible en el tablero.
        
        if not vehiculo.camino_restante:
            return False
            
        destino = vehiculo.camino_restante[-1]
        
        recurso = self.tablero.pos_recursos.get(destino)
        
        return recurso is not None and recurso.estado == "disponible" and recurso.categoria in vehiculo.tipo_carga_permitida
"""
        

