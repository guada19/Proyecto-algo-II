from src.aircraft import *
from src.mines import *
from src.resources import *
from src.base import *
import random
import copy
import pygame


class Tablero:
    def __init__(self, ancho, largo):
        self.ancho = ancho
        self.largo = largo
        self.matriz = [["0" for _ in range(ancho)] for _ in range(largo)]
        self.vehiculos = []
        self.recursos = []
        self.minas = []
        self.pos_recursos = {}  
        self.pos_minas = {}
        self.posiciones_ocupadas = set()
        # celdas reservadas por el alcance de minas (no se puede colocar elemento ahí)
        self.reserved_positions = set()
        
        # Simulación y Historial
        # Estado: 'stopped', 'init', 'running', 'paused'
        self.sim_state = "stopped" 
        self.historial_matrices = [] 
        self.indice_historial = 0

        # Posiciones de colisión visibles SOLO durante el paso en que ocurren
        # (se almacena un set de tuplas (fila, col))
        self.colisiones_visible = set()
        # Colisiones que acaban de ocurrir (se usan para reproducir sonido 1 vez)
        self.colisiones_just_added = set()

        # Flag para mostrar overlay de "juego finalizado" cuando se presiona STOP
        self.game_finished = False

        # Inicializamos las bases (usar atributos del objeto, no variables locales)
        self.base_jugador1 = Base(self.ancho, self.largo, 1, [])
        self.base_jugador2 = Base(self.ancho, self.largo, 2, [])
        self.bases = {1: self.base_jugador1, 2: self.base_jugador2}
        # Asegurar estado inicial vacío en la matriz e historial (guardado como frame estructurado)
        self.actualizar_matriz()
        #self.historial_matrices = []
        #self.indice_historial = 0
        # Guardar primer frame estructurado
        self._guardar_estado_en_historial()
        # contador de pasos de simulación (se incrementa en ejecutar_un_paso_simulacion)
        self.step_count = 0

    def _influence_positions(self, tipo, pos, radio):
        """Retorna set de celdas (fila,col) que constituyen el área de influencia
        del tipo de mina colocado en pos.
        - Siempre recorta la influencia al área cuadriculada central (columnas 1 .. ancho-2).
        - Recorta también a los límites de filas (0 .. largo-1)."""
        x, y = pos
        influ = set()
        # columnas válidas de la grilla central (excluyen las columnas de base 0 y ancho-1)
        col_min = 1
        col_max = max(1, self.ancho - 2)

        if tipo in ("01", "02", "G1"):
            # circular: incluir celdas cuya distancia euclídea <= radio,
            # pero limitar columnas a [col_min, col_max]
            r = int(max(0, radio))
            row_min = max(0, x - r)
            row_max = min(self.largo - 1, x + r)
            col_start = max(col_min, y - r)
            col_end = min(col_max, y + r)
            for i in range(row_min, row_max + 1):
                for j in range(col_start, col_end + 1):
                    dx = i - x
                    dy = j - y
                    if dx*dx + dy*dy <= r*r:
                        influ.add((i, j))

        elif tipo == "T1":
            # horizontal span ±radio, pero solo dentro de columnas centrales
            span = int(max(0, radio))
            left = max(col_min, y - span)
            right = min(col_max, y + span)
            if 0 <= x < self.largo:
                for j in range(left, right + 1):
                    influ.add((x, j))

        elif tipo == "T2":
            # vertical span ±radio, column must be within central columns
            if not (col_min <= y <= col_max):
                return influ
            span = int(max(0, radio))
            top = max(0, x - span)
            bottom = min(self.largo - 1, x + span)
            for i in range(top, bottom + 1):
                influ.add((i, y))

        return influ

    def add_collision(self, pos):
        """Registrar colisión en pos (fila, col) — se mantiene hasta el siguiente paso."""
        tpos = tuple(pos)
        self.colisiones_visible.add(tpos)
        self.colisiones_just_added.add(tpos)

    # --- Métodos de Control de la Simulación ---
    def set_sim_state(self, new_state):
        """Establece el estado de la simulación y realiza acciones de inicio/parada."""
        if new_state == "init":
             # Inicializa la simulación (poblar elementos) y quitar overlay de "juego finalizado"
             self.game_finished = False
             self.initialization_simulation()
             self.sim_state = "running" # Inicia corriendo automáticamente
        elif new_state == "stopped":
            # Detener la simulación y limpiar TODOS los elementos visibles
            self.sim_state = "stopped"
            self.vehiculos = []
            self.recursos = []
            self.minas = []
            self.pos_recursos = {}
            self.pos_minas = {}
            self.posiciones_ocupadas = set()
            # actualizar matriz a estado vacío y guardar en historial
            self.actualizar_matriz()
            self.historial_matrices = [copy.deepcopy(self.matriz)]
            self.indice_historial = 0
            # activar overlay de "juego finalizado"
            self.game_finished = True
        else:
            self.sim_state = new_state
            
    def toggle_sim_state(self):
        """Alterna entre running y paused."""
        if self.sim_state == "running":
            self.sim_state = "paused"
        elif self.sim_state == "paused":
            self.sim_state = "running"
        elif self.sim_state == "init": # Si se presiona antes de que inicie la simulación
            self.initialization_simulation()
            self.sim_state = "paused"
        
    def _guardar_estado_en_historial(self):
        """Guarda la matriz actual como una nueva entrada en el historial."""
        # Si estamos "atrás" en el historial, borramos el futuro antes de añadir uno nuevo
        if self.indice_historial < len(self.historial_matrices) - 1:
            self.historial_matrices = self.historial_matrices[:self.indice_historial + 1]

        # Construir frame con overlays (copias, para que el historial sea inmutable)
        frame = {
            "matriz": copy.deepcopy(self.matriz),
            "colisiones": set(self.colisiones_visible),
            "colisiones_just_added": set(self.colisiones_just_added),
            "minas_overlay": [],
            "step_count": int(getattr(self, "step_count", 0))
        }
        # Registrar estado/visibilidad de cada mina en el frame
        for m in self.minas:
            frame["minas_overlay"].append({
                "pos": (m.x, m.y),
                "tipo": getattr(m, "tipo", None),
                "estado": getattr(m, "estado", None),
                "radio": int(getattr(m, "radio", 0)),
                # visibilidad de G1 depende del contador de pasos en ese momento
                "visible": (getattr(m, "tipo", None) != "G1") or (((self.step_count // 5) % 2) == 0 and getattr(m, "estado", None) == "activa")
            })

        self.historial_matrices.append(frame)
        self.indice_historial = len(self.historial_matrices) - 1
        # limpiar las colisiones "just added" en el estado vivo (el frame ya las contiene)
        self.colisiones_just_added = set()
        # ...existing code...

    def obtener_frame_actual(self):
        """Retorna el frame completo (matriz + overlays) correspondiente al índice actual."""
        if not self.historial_matrices:
            return {
                "matriz": copy.deepcopy(self.matriz),
                "colisiones": set(),
                "colisiones_just_added": set(),
                "minas_overlay": []
            }
        entry = self.historial_matrices[self.indice_historial]
        # compatibilidad: si la entrada es una matriz antigua (list), envolverla en frame
        if isinstance(entry, list):
            return {
                "matriz": copy.deepcopy(entry),
                "colisiones": set(),
                "colisiones_just_added": set(),
                "minas_overlay": []
            }
        return entry

    def obtener_matriz_historial(self):
        """Compatibilidad: retorna solo la matriz del frame actual (método usado anteriormente)."""
        frame = self.obtener_frame_actual()
        return frame.get("matriz", self.matriz)

    def prev_frame(self):
        """Retrocede un paso en el historial (Botón <<)."""
        if self.indice_historial > 0:
            self.indice_historial -= 1
            # Forzar la pausa al moverse en el historial
            if self.sim_state == "running":
                self.sim_state = "paused"

    def next_frame(self):
        """Avanza un paso en el historial (Botón >>)."""
        if self.indice_historial < len(self.historial_matrices) - 1:
            self.indice_historial += 1
            # Forzar la pausa al moverse en el historial
            if self.sim_state == "running":
                self.sim_state = "paused"
        elif self.sim_state == "running":
             # Si estamos al final y la simulación está corriendo, realiza el siguiente paso
             self.ejecutar_un_paso_simulacion()
             
        
    # --- Métodos de Simulación ---

    def _crear_elementos(self):
        """Genera y retorna la lista de 65 objetos Resource y Mine."""
        elementos = []
        
        # 10 Personas
        elementos.extend([Person() for _ in range(10)]) 
        
        # 50 Mercancías
        elementos.extend([Alimento() for _ in range(12)]) 
        elementos.extend([Ropa() for _ in range(12)]) 
        elementos.extend([Medicamento() for _ in range(13)])
        elementos.extend([Armamento() for _ in range(13)])
        
        # 5 Minas 
        elementos.append(MinesCircularesEstaticas(tipo=1))
        elementos.append(MinesCircularesEstaticas(tipo=2)) 
        elementos.append(MinesLinealesEstaticas(tipo=1)) 
        elementos.append(MinesLinealesEstaticas(tipo=2)) 
        elementos.append(MineG1())
        
        return elementos

    def inicializar_elementos_aleatoriamente(self):
        """
        Genera los recursos y minas, les asigna una posición aleatoria (evitando las bases)
        y los almacena en las listas y diccionarios del tablero.

        Nueva estrategia:
        - limpiar estructuras
        - separar minas y recursos
        - crear lista de posiciones candidatas (excluyendo columnas de bases)
        - colocar minas primero (reservando su área de influencia)
        - luego colocar recursos en posiciones libres restantes
        - si no hay posiciones válidas se lanza RuntimeError con mensaje claro
        """
        self.recursos = []
        self.minas = []
        self.pos_recursos = {}
        self.pos_minas = {}
        self.posiciones_ocupadas = set()
        self.reserved_positions = set()  # limpiar reservas previas

        elementos = self._crear_elementos()

        # Separar minas y recursos para colocar minas primero
        minas = [e for e in elementos if isinstance(e, Mine)]
        recursos = [e for e in elementos if isinstance(e, Resource)]

        # Posiciones candidatas (excluir columna 0 y columna ancho-1 usadas por bases)
        y_min = 1
        y_max = self.ancho - 2
        all_positions = [(i, j) for i in range(0, self.largo) for j in range(y_min, y_max + 1)]

        # Helper para elegir aleatoriamente desde una lista
        def elegir_aleatoria(lst):
            if not lst:
                return None
            return random.choice(lst)

        # 1) Colocar minas primero (reservar sus zonas)
        for mina in minas:
            # calcular posiciones válidas para esta mina
            valid = []
            for pos in all_positions:
                if pos in self.posiciones_ocupadas:
                    continue
                if pos in self.reserved_positions:
                    continue
                tipo = getattr(mina, "tipo", None)
                radio = int(getattr(mina, "radio", 0))
                influ = self._influence_positions(tipo, pos, radio)
                # no debe intersectar ocupadas ni reservas existentes
                if influ & self.posiciones_ocupadas:
                    continue
                if influ & self.reserved_positions:
                    continue
                valid.append(pos)
            pos = elegir_aleatoria(valid)
            if pos is None:
                raise RuntimeError("No hay posiciones válidas para colocar todas las minas. Reduce densidad o aumenta el tablero.")
            mina.x, mina.y = pos
            self.minas.append(mina)
            self.pos_minas[pos] = mina
            # reservar influencia para futuras colocaciones
            tipo = getattr(mina, "tipo", None)
            radio = int(getattr(mina, "radio", 0))
            influ = self._influence_positions(tipo, pos, radio)
            self.reserved_positions.update(influ)
            # reservar la celda concreta también
            self.posiciones_ocupadas.add(pos)

        # 2) Colocar recursos en posiciones que no estén ocupadas ni reservadas
        free_positions = [p for p in all_positions if p not in self.posiciones_ocupadas and p not in self.reserved_positions]
        if len(free_positions) < len(recursos):
            raise RuntimeError("No hay suficientes posiciones libres para colocar todos los recursos. Reduce elementos o aumenta tablero.")

        random.shuffle(free_positions)
        for recurso, pos in zip(recursos, free_positions):
            recurso.x, recurso.y = pos
            self.recursos.append(recurso)
            self.pos_recursos[pos] = recurso
            self.posiciones_ocupadas.add(pos)

        # nota: no tocamos vehículos aquí (se inicializan en inicializar_vehiculos)
    
    def inicializar_vehiculos(self):
        tipos = [(Jeep, 3),(Moto, 2),(Camion, 2), (Auto, 3)]
        self.vehiculos = []
        Vehiculo.filas_por_jugador = {1: 0, 2: 0}
        # asegurarse de no mostrar colisiones previas al repoblar
        self.colisiones_visible = set()

        for clase, cantidad in tipos:
            for jugador in (1, 2):
                base_actual = self.bases[jugador]
                for _ in range(cantidad):
                    if jugador == 1:
                        x = Vehiculo.filas_por_jugador[1]
                        y = 0
                        Vehiculo.filas_por_jugador[1] += 1
                    else:
                        x = Vehiculo.filas_por_jugador[2]
                        y = self.ancho-1
                        Vehiculo.filas_por_jugador[2] += 1
                
                    nuevo_vehiculo = clase(posicion=(x, y), jugador=jugador)
                    base_actual.vehiculos.append(nuevo_vehiculo)
                    self.vehiculos.append(nuevo_vehiculo)  
        self.actualizar_matriz()

    
    def initialization_simulation(self):
        """Inicializa los elementos del tablero, vehículos y el historial."""
        # quitar cualquier overlay de "juego finalizado" si existía
        self.game_finished = False
        # limpiar colisiones previas al iniciar nuevo juego
        self.colisiones_visible = set()
        # poblar elementos y vehículos
        self.inicializar_elementos_aleatoriamente()
        self.inicializar_vehiculos()
        self.actualizar_matriz()
        # reiniciar historial y guardar estado inicial poblado
        self.historial_matrices = []
        self.indice_historial = 0
        self._guardar_estado_en_historial() # Guardar el estado inicial
        # reiniciar contador de pasos al iniciar la simulación
        self.step_count = 0
        self.mostrar_tablero()
        
    def ejecutar_un_paso_simulacion(self):
        """Ejecuta un paso de la simulación (movimiento de vehículos)."""
        # Limpiar colisiones previas: la estrella de colisión solo debe mostrarse
        # durante el paso en el que se detecta la colisión, por eso borramos
        # las marcas al inicio del siguiente paso.
        self.colisiones_visible = set()

        if self.sim_state not in ("running", "init"):
            return 
        
        # Mover vehículos 
        for v in self.vehiculos:
            if v.estado == "activo":
                v.ejecutar_estrategia(self) 
        # Detectar colisiones: posiciones con >1 vehículo
        # Sólo incluir vehículos activos para detectar colisiones.
        posiciones = {}
        for v in self.vehiculos:
            if v.estado != "activo":
                continue
            pos = v.posicion
            posiciones.setdefault(pos, []).append(v)

        for pos, lista in posiciones.items():
            if len(lista) > 1:
                # marcar colisión: los vehículos dejan de mostrarse (destruidos)
                for v in lista:
                    v.destruir()  # cambia estado a "destruido"
                    # eliminar de la base si estaba registrada (opcional, evita duplicados)
                    try:
                        base = self.bases.get(v.jugador)
                        if base and v in base.vehiculos:
                            base.vehiculos.remove(v)
                    except Exception:
                        pass
                # registrar la posición de colisión VISIBLE (durará hasta el próximo paso)
                self.add_collision(pos)

        # --- Detectar colisiones vehículo <-> mina ---
        # Recorremos vehículos activos y minas activas; si vehículo cae en el área de influencia
        # de una mina, ambos se eliminan y la carga del vehículo se destruye.
        for v in list(self.vehiculos):
            if v.estado != "activo":
                continue
            vpos = v.posicion
            for m in list(self.minas):
                if getattr(m, "estado", None) != "activa":
                    continue
                # área de influencia de la mina (set de (fila,col))
                influ = self._influence_positions(getattr(m, "tipo", None), (m.x, m.y), int(getattr(m, "radio", 0)))
                if vpos in influ:
                    # destruir vehículo y su carga
                    try:
                        for carga in list(getattr(v, "carga_actual", [])):
                            # si el recurso tiene método destruirse, usarlo
                            if hasattr(carga, "destruirse"):
                                carga.destruirse()
                        v.carga_actual = []
                    except Exception:
                        v.carga_actual = []
                    v.destruir()
                    # eliminar de la base si estaba allí
                    try:
                        base = self.bases.get(v.jugador)
                        if base and v in base.vehiculos:
                            base.vehiculos.remove(v)
                    except Exception:
                        pass

                    # destruir la mina: marcar estado y liberar reservas/posiciones
                    try:
                        m.estado = "destruida"
                    except Exception:
                        m.estado = "destruida"
                    # liberar reservas asociadas a la mina
                    try:
                        radio = int(getattr(m, "radio", 0))
                        influ_m = self._influence_positions(getattr(m, "tipo", None), (m.x, m.y), radio)
                        self.reserved_positions.difference_update(influ_m)
                    except Exception:
                        pass
                    # remover mapa de minas
                    try:
                        pos_m = (m.x, m.y)
                        self.pos_minas.pop(pos_m, None)
                        # mantener en self.minas pero con estado "destruida" (opcional: eliminar completamente)
                    except Exception:
                        pass

                    # registrar colisión visual y sonora en la celda del vehículo/mina
                    self.add_collision(vpos)
                    # ya manejamos este vehículo con esta mina -> salir del bucle de minas
                    break

        # (Opcional) limpiar vehículos destruidos de la lista para evitar efectos secundarios
        # pero mantenerlos si quieres histórico; aquí los mantenemos pero con estado 'destruido'
        # self.vehiculos = [v for v in self.vehiculos if v.estado == "activo"]



        # Actualizar matriz
        self.actualizar_matriz()

        # avanzar contador de pasos ANTES de guardar el frame para que el frame refleje el paso actual
        try:
            self.step_count += 1
        except Exception:
            self.step_count = getattr(self, "step_count", 0) + 1

        # Guardar el nuevo estado en el historial 
        self._guardar_estado_en_historial()
        # Se asegura de estar al final del historial
        self.indice_historial = len(self.historial_matrices) - 1

        # Si alcanzamos 60 pasos, detener la simulación igual que si se presionara STOP
        if getattr(self, "step_count", 0) >= 60:
            # set_sim_state('stopped') ejecuta la limpieza y muestra overlay de "juego finalizado"
            self.set_sim_state("stopped")
            return

    def start_simulation(self):
        pass

    def actualizar_matriz(self):
        # 1. Limpiar matriz
        self.matriz = [["0" for _ in range(self.ancho)] for _ in range(self.largo)]

        # 2. Poner Minas 
        for m in self.minas:
            if m.estado == "activa": 
                x, y = m.x, m.y
                if 0 <= x < self.largo and 0 <= y < self.ancho:
                    self.matriz[x][y] = m.tipo

        # 3. Poner Recursos (solo disponibles en el diccionario)
        for pos, r in self.pos_recursos.items():
            if r.estado == "disponible":
                x, y = pos
                if 0 <= x < self.largo and 0 <= y < self.ancho:
                    if r.categoria == "persona":
                         self.matriz[x][y] = 'PER'
                    elif r.subtipo == "alimento":
                         self.matriz[x][y] = 'R' # Usamos R de Recurso (Alimento)
                    else:
                         self.matriz[x][y] = r.subtipo[0] # r (ropa), m (medicamento), a (armamento)
                    
        # 4. Poner Vehículos (Debe ir último para que sobrescriba)
        # Asegura que solo se muestren los vehículos activos, incluyendo los que están en la base. (Punto 1 y 2)
        for v in self.vehiculos:
            if v.estado == "activo":
                x, y = v.posicion
                if 0 <= x < self.largo and 0 <= y < self.ancho:
                     self.matriz[x][y] = v.label # Usa la nueva etiqueta (Ej: J1, M2, A1) (Punto 3)

    def actualizar_matriz_parcial(self):
        pass

    def mostrar_tablero(self):
        for fila in self.matriz:
            print(" ".join(f"[{celda}]" for celda in fila))