from src.pathfinding import a_star, bfs_path, bfs_recurso_mas_cercano


class Estrategia_J1:

    
    #Estrategia simple para J1:
    # Al IR a recursos: usa BFS ignorando minas (para detonarlas y no evitarlas).
    # Al VOLVER a base: usa A* (evita minas) para no perder la carga.
   

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

        self._reactivar_si_puede(vehiculo)     

        if not hasattr(vehiculo, "camino_restante"):
            vehiculo.camino_restante = []
        if not hasattr(vehiculo, "objetivo_recurso"):
            vehiculo.objetivo_recurso = None

        # ------------------- VOLVER A BASE (A*) -------------------
        if len(vehiculo.carga_actual) == vehiculo.capacidad_carga or vehiculo.viajes_restantes <= 0:

            col_base = 0 if vehiculo.jugador in (1, "J1") else self.tablero.ancho - 1
            objetivo = (vehiculo.posicion[0], col_base)

            if vehiculo.posicion == objetivo:
                vehiculo.camino_restante = []
                return None

            # (Re)planificar A* sólo si no hay camino o cambió el objetivo
            if not vehiculo.camino_restante or vehiculo.camino_restante[-1] != objetivo:
                self.desasignar_recurso(vehiculo)
                camino = a_star(vehiculo, self.tablero, objetivo)
                vehiculo.camino_restante = camino[1:] if camino else []

            # Validar siguiente paso (evitar minas/ocupaciones al volver)
            if vehiculo.camino_restante:
                next_pos = vehiculo.camino_restante[0]
                # Evitar aliados
                if self._aliado_ocupa_o_intenta(next_pos, vehiculo):
                    # Plan B: paso lateral que evite aliados y minas (estamos volviendo cargados)
                    lateral = self._paso_lateral_libre(vehiculo, objetivo, ignorar_minas=False)
                    if lateral:
                        return lateral
                    # Sin salida: replanear y no mover
                    vehiculo.camino_restante = []
                    return None
                # Evitar minas al volver
                if self.tablero.colision_minas(*next_pos):
                    vehiculo.camino_restante = []
                    return None
                
                return vehiculo.camino_restante.pop(0)

            return None

        # ------------------- IR A RECURSOS (BFS ignorando minas) -------------------
        # Cada N steps podés liberar asignación para evitar “atascos” (opcional)
        if getattr(self.tablero, "step_count", 0) % 5 == 0:
            # Si querés ser más conservador, comentá estas dos líneas
            self.desasignar_recurso(vehiculo)
            vehiculo.camino_restante = []

        # Si el recurso actual ya no sirve, reset
        if not self.recurso_objetivo_valido(vehiculo):
            self.desasignar_recurso(vehiculo)

        # Elegir recurso por BFS (ignora minas) si no hay objetivo
        if vehiculo.objetivo_recurso is None:
            recurso_objetivo = bfs_recurso_mas_cercano(vehiculo, self.tablero, ignore_mines=True)
            if recurso_objetivo is None:
                return None
            vehiculo.objetivo_recurso = recurso_objetivo

        objetivo = vehiculo.objetivo_recurso

        # Chequeo opcional de next_pos contra vehículos (NO chequeamos minas aquí a propósito)
        if vehiculo.camino_restante:
            next_pos = vehiculo.camino_restante[0]
            # No pisar aliados (pero seguimos ignorando minas aquí)
            if self._aliado_ocupa_o_intenta(next_pos, vehiculo):
                lateral = self._paso_lateral_libre(vehiculo, vehiculo.objetivo_recurso, ignorar_minas=True)
                if lateral:
                    # al hacer paso lateral, descartamos el plan viejo para replanear luego
                    vehiculo.camino_restante = []
                    return lateral
                vehiculo.camino_restante = []
                return None

        # Si no hay camino, o se vació, o cambió el objetivo → planificar BFS ignorando minas
        if not vehiculo.camino_restante or vehiculo.camino_restante[-1] != objetivo:
            camino = bfs_path(self.tablero, vehiculo.posicion, objetivo, ignore_mines=True)
            if not camino or len(camino) < 2:
                # Si no hay camino viable, liberamos el recurso y no nos movemos este tick
                if vehiculo.objetivo_recurso is not None:
                    self.desasignar_recurso(vehiculo)
                return None
            vehiculo.camino_restante = camino[1:]

        # Ejecutar siguiente paso (sin chequear minas: queremos detonarlas)
        return vehiculo.camino_restante.pop(0) if vehiculo.camino_restante else None

    def desasignar_recurso(self, vehiculo):
        if hasattr(vehiculo, 'objetivo_recurso') and vehiculo.objetivo_recurso:
            recurso_pos = vehiculo.objetivo_recurso
            recurso = self.tablero.pos_recursos.get(recurso_pos)
            if recurso and getattr(recurso, "asignado_a", None) == vehiculo:
                recurso.asignado_a = None
        vehiculo.camino_restante = []
        vehiculo.objetivo_recurso = None

    def recurso_objetivo_valido(self, vehiculo):

        if vehiculo.objetivo_recurso is None:
            return False
        recurso = self.tablero.pos_recursos.get(vehiculo.objetivo_recurso)
        return (
            recurso is not None
            and recurso.estado == "disponible"
            and recurso.categoria in vehiculo.tipo_carga_permitida
            and getattr(recurso, "asignado_a", None) in (None, vehiculo)
        )
    
    def _aliado_ocupa_o_intenta(self, pos, vehiculo):
        x, y = pos
        # En columnas de base el motor ya trata especial; no frenamos por aliados allí
        if y == 0 or y == self.tablero.ancho - 1:
            return False
        for v in self.tablero.vehiculos:
            if v is vehiculo:
                continue
            if v.estado != "activo":
                continue
            if v.jugador != vehiculo.jugador:   # solo aliados
                continue
            if v.posicion == (x, y) or getattr(v, "posicion_intencionada", None) == (x, y):
                return True
        return False

    def _paso_lateral_libre(self, vehiculo, objetivo, ignorar_minas=False):
        #Devuelve una celda vecina libre (sin aliado) que acerque al objetivo. Si ninguna mejora distancia, devuelve la primera vecina válida; si no hay, None.
        x, y = vehiculo.posicion
        candidatos = [(x+1,y), (x-1,y), (x,y+1), (x,y-1)]
        ancho, largo = self.tablero.ancho, self.tablero.largo

        def walkable(nx, ny):
            if not (0 <= nx < ancho and 0 <= ny < largo):
                return False
            # paredes / impasables duros
            if hasattr(self.tablero, "es_bloqueante") and self.tablero.es_bloqueante(nx, ny):
                return False
            if hasattr(self.tablero, "colision_pared") and self.tablero.colision_pared(nx, ny):
                return False
            # minas: solo evitamos si no queremos kamikaze
            if not ignorar_minas and hasattr(self.tablero, "colision_minas") and self.tablero.colision_minas(nx, ny):
                return False
            # aliados: no pisar ocupación ni intención aliada
            if self._aliado_ocupa_o_intenta((nx, ny), vehiculo):
                return False
            return True

        validas = [(nx, ny) for (nx, ny) in candidatos if walkable(nx, ny)]
        if not validas:
            return None

        # ordenar por distancia al objetivo (más cerca primero)
        def manhattan(a, b): return abs(a[0]-b[0]) + abs(a[1]-b[1])
        validas.sort(key=lambda p: manhattan(p, objetivo) if objetivo else 0)

        # ideal: que acerque al objetivo respecto de la actual
        if objetivo:
            d0 = manhattan((x, y), objetivo)
            for p in validas:
                if manhattan(p, objetivo) < d0:
                    return p

        # si ninguna mejora, devuelve la primera válida (para destrabar)
        return validas[0]

    def _reactivar_si_puede(self, vehiculo):
        
        #Si el vehículo está en base, sin carga, con viajes disponibles y sin ruta/objetivo, elige un nuevo recurso y arma un camino para salir nuevamente.
        
        # Requisitos
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

        # 1) Elegir recurso más cercano (ignorando minas para ir)
        objetivo = None
        try:
            # firma con flags (si tu helper la soporta)
            objetivo = bfs_recurso_mas_cercano(vehiculo, self.tablero, ignore_mines=True)
        except TypeError:
            # firma sin flags
            try:
                objetivo = bfs_recurso_mas_cercano(vehiculo, self.tablero, self.jugador)
            except TypeError:
                objetivo = bfs_recurso_mas_cercano(vehiculo, self.tablero)

        if not objetivo:
            return

        vehiculo.objetivo_recurso = objetivo

        # 2) Armar camino con BFS (ignorando minas para ir)
        path = []
        try:
            path = bfs_path(self.tablero, origen, objetivo, ignore_mines=True)
        except TypeError:
            path = bfs_path(self.tablero, origen, objetivo)

        vehiculo.camino_restante = path or []
