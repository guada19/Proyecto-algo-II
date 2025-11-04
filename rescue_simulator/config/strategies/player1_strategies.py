from src.pathfinding import a_star, bfs_path, bfs_recurso_mas_cercano

def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


class Estrategia_J1:

    """
    Estrategia simple para J1:
    - Al IR a recursos: usa BFS ignorando minas (para detonarlas y no evitarlas).
    - Al VOLVER a base: usa A* (evita minas) para no perder la carga.
    - Mantiene compatibilidad con la interfaz/flujo del jugador 2 (camino_restante / objetivo_recurso).
    """

    def __init__(self, jugador, base, tablero):
        self.jugador = jugador
        self.base = base
        self.tablero = tablero

    def obtener_siguiente_paso(self, vehiculo):

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
                if self.tablero.colision_vehiculos_para_a_star(*next_pos) or self.tablero.colision_minas(*next_pos):
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
            if self.tablero.colision_vehiculos_para_a_star(*next_pos):
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