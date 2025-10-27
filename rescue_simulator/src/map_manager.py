from src.aircraft import *
from src.mines import *
from src.resources import *
from src.base import *
from config.strategies.player2_strategies import Estrategia
import random
import copy



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
        
        # Inicializamos las bases
        self.base_jugador1 = Base(ancho, largo, 1, [])
        self.base_jugador2 = Base(ancho, largo, 2, [])
        self.bases = {1: self.base_jugador1, 2: self.base_jugador2}

        #Puntaje por jugador (izq = J1, der = J2)
        self.puntaje = {"J1": 0, "J2": 0} #Contador de puntos de cada jugador
        self.entregas = {"J1": 0, "J2": 0} #Contador de ítems entregados

        # Simulación y Historial
        # Estado: 'stopped', 'init', 'running', 'paused'
        self.sim_state = "stopped" 
        self.historial_matrices = [] 
        self.indice_historial = 0

        # contador de pasos de simulación 
        self.step_count = 0

        #Nuevo
        #Rutas por vehiculo
        self.path_ida = {}     # v -> [(x,y), ...] camino acumulado de ida
        self.ruta_activa = {}  # v -> [(x,y), ...] ruta que está siguiendo ahora (ida o regreso)
        self.ruta_idx = {}     # v -> índice en la ruta actual
        self.returning = set() # {v} vehículos en modo regreso a base
    
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
        Distribuye aleatoriamente recursos y minas en el mapa sin superposición.
        Agregué un diccionario para poder acceder a las minas y recursos de manera más directa
        y la añadi al tablero ya que antes estaba definida por afuera y no estaban inicializados los objetos jeje
        """
        
        self.recursos = []
        self.minas = []
        self.pos_recursos = {} 
        self.pos_minas = {}
        self.posiciones_ocupadas = set() 
        
        elementos = self._crear_elementos()
        
        # Defini en que posiciones se pueden asignar los recursos evitando las bases de los jugadores
        # Bases están en la columna 0 y columna ancho-1 (y=0 y y=ancho-1)
        y_min = 1
        y_max = self.ancho - 2 
        
        # 3. Asignar Posición Aleatoria y Almacenar
        for elemento in elementos:
            posicion_valida = False
            while not posicion_valida:
                
                x = random.randint(0, self.largo - 1)
                y = random.randint(y_min, y_max) 
                pos = (x, y)
                
                if pos not in self.posiciones_ocupadas:
                    
                    elemento.x, elemento.y = pos 
                    self.posiciones_ocupadas.add(pos)
                    posicion_valida = True
            
            if isinstance(elemento, Resource):
                self.recursos.append(elemento)
                self.pos_recursos[pos] = elemento 
            
            elif isinstance(elemento, Mine):
                self.minas.append(elemento)
                self.pos_minas[pos] = elemento
    
    
    def inicializar_vehiculos(self):
        tipos = [(Jeep, 3),(Moto, 2),(Camion, 2), (Auto, 3)]
        self.vehiculos = []
        Vehiculo.filas_por_jugador = {1: 0, 2: 0}

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
                
                    nuevo_vehiculo = clase(posicion=(x, y), jugador=("J1" if jugador==1 else "J2"))
                    base_actual.vehiculos.append(nuevo_vehiculo)
                    self.vehiculos.append(nuevo_vehiculo) 
        self.actualizar_matriz()

    #-----------------------------------------------------------------------------------------------------------
    """
    esto es solo para probar que el movimiento funcione de manera correcta, no sé en donde va a estar lo de las colisiones
    así que lo puse acá nada más para probar no es nada muy interesante después se borra
    """
    def colision_minas(self, x, y):
    # Devuelve True si la celda está dentro del radio de alguna mina
    # Para simplificar, asumimos radio=1
        for mx, my in self.pos_minas:
            if abs(mx - x) <= 1 and abs(my - y) <= 1:
                return True
        return False

    def colision_vehiculos(self, x, y):
        # Para este ejemplo, asumimos que no hay otros vehículos
        return False
    #------------------------------------------------------------------------------------------------------------
    
    def initialization_simulation(self):
        self.inicializar_elementos_aleatoriamente()
        self.inicializar_vehiculos()
        self.actualizar_matriz()
        self.mostrar_tablero()
        
         
    def start_simulation(self):
        #Acá es donde cada jugador debería ejecutar su propia estrategia
        estrategia_j2 = Estrategia(self.bases[2].jugador, self.bases[2], self)
        self.bases[2].asignar_estrategia(estrategia_j2)
        estrategia_j2.ejecutar_estrategia()
        
        #NUEVO
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
                    self.matriz[x][y] = 'P' if r.categoria == "persona" else r.subtipo[0] 
                    
        # 4. Poner Vehículos (Debe ir último para que sobrescriba)
        for v in self.vehiculos:
            x, y = v.posicion
            if 0 <= x < self.largo and 0 <= y < self.ancho:
                 self.matriz[x][y] = v.tipo[0]

    def actualizar_matriz_parcial(self):
        for v in self.vehiculos:
            x_ant, y_ant = v.posicion_anterior
            if (x_ant, y_ant) in self.pos_recursos and self.pos_recursos[(x_ant, y_ant)].estado == "disponible":
                # El recurso todavía está ahí, no borramos nada
                pass
            else:
                self.matriz[x_ant][y_ant] = "0"
        
        for v in self.vehiculos:
            x, y = v.posicion
            self.matriz[x][y] = v.tipo[0]

    def mostrar_tablero(self):
        for fila in self.matriz:
            print(" ".join(f"[{celda}]" for celda in fila))
        
        print("")
        print("")
        print("")
        print("")



    #función para saber si la columna del tablero es base
    def es_base(self, col):
        if col == 0:
            return "J1"
        if col == self.ancho - 1:
            return "J2"
        return None
    

    #función para saber cuantos puntos vale cada item entregado
    def puntos_por (self, item):
        categoria = getattr(item, "categoria", None)
        subtipo = getattr(item, "subtipo", None)

        if categoria == "persona":
            return 50
        
        if categoria == "mercancia":
            tabla = {
            "alimento": 10,
            "ropa": 5,
            "medicamento": 20,
            "armamento": 50,
            }
            if subtipo:
                return tabla.get(subtipo.lower(), 10)
            return 10
    
        return 5


    #función que registra la entrega cuando llega a la base el vehiculo
    def registrar_entrega(self, vehiculo):
        #verifica si el vehiculo está en una base
        x, y = vehiculo.posicion
        base = self.es_base(y)
        if base is None:
            return
        
        # Verificar base y jugador correcto
        if vehiculo.jugador != base:
            return

        if not vehiculo.carga_actual:
            return  # No tiene carga

        total = 0
        for item in vehiculo.carga_actual:
            total += self.puntos_por(item)

        self.puntaje[base] += total
        self.entregas[base] += len(vehiculo.carga_actual)

        vehiculo.carga_actual.clear()
        print(f"{base} entregó carga (+{total} pts). Total: {self.puntaje[base]}")

        self.actualizar_matriz()
        # asegurarnos de guardar el estado en historial (así el cambio se ve)
        try:
            self._guardar_estado_en_historial()
            self.indice_historial = len(self.historial_matrices) - 1
        except Exception:
            pass



#---Funciones que se quedan ---

    # --- Métodos de Control de la Simulación ---
    def set_sim_state(self, new_state):
        """Establece el estado de la simulación y realiza acciones de inicio/parada."""
        if new_state == "init":
             # Inicializa la simulación (poblar elementos) y quitar overlay de "juego finalizado"
             self.game_finished = False
             self.initialization_simulation()
             self.sim_state = "paused" # Inicia corriendo automáticamente
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
#            "colisiones": set(self.colisiones_visible),
#            "colisiones_just_added": set(self.colisiones_just_added),
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
#                "colisiones": set(),
#                "colisiones_just_added": set(),
                "minas_overlay": []
            }
        entry = self.historial_matrices[self.indice_historial]
        # compatibilidad: si la entrada es una matriz antigua (list), envolverla en frame
        if isinstance(entry, list):
            return {
                "matriz": copy.deepcopy(entry),
#               "colisiones": set(),
#                "colisiones_just_added": set(),
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


    #NUEVOOO
    #Regreso a base funcional, pero para eso necesito la ruta de pathfinding pero para eso necesito ejecutar la simulacion pero para eso ...}
    """Mi intención acá era que al asignar la ruta el vehiculo guarde el camino que esta recorriendo, y que para volver
        a la base, recorra exactamente el mismo camino pero a la inversa"""
    # ===================== RUTAS / REGRESO =====================

    def _veh_key(self, v):
        return v  # usamos el propio objeto como key

    def asignar_ruta(self, vehiculo, ruta):
        """
        Fija una ruta de A* para el vehículo y la ACUMULA en path_ida (ida).
        """
        k = self._veh_key(vehiculo)
        if not ruta:
            self.ruta_activa.pop(k, None)
            self.ruta_idx.pop(k, None)
            return

        # Alinear: que arranque en la posición actual
        if ruta[0] != vehiculo.posicion:
            ruta = [vehiculo.posicion] + ruta

        self.ruta_activa[k] = ruta
        self.ruta_idx[k] = 0

        # Acumular en path_ida sin duplicar
        pi = self.path_ida.get(k, [])
        if not pi:
            pi = [ruta[0]]
        start = 1 if pi and pi[-1] == ruta[0] else 0
        pi.extend(ruta[start:])
        self.path_ida[k] = pi

        # Si estaba volviendo, cancelo regreso (hay nueva ida)
        self.returning.discard(k)

    def tiene_ruta(self, vehiculo):
        k = self._veh_key(vehiculo)
        ruta = self.ruta_activa.get(k)
        idx = self.ruta_idx.get(k, 0)
        return bool(ruta) and idx < len(ruta) - 1

    def _step_ruta(self, vehiculo):
        """Avanza un paso en la ruta activa (ida o regreso). True si se movió."""
        k = self._veh_key(vehiculo)
        ruta = self.ruta_activa.get(k)
        idx = self.ruta_idx.get(k, 0)
        if not ruta or idx >= len(ruta) - 1:
            return False

        nx, ny = ruta[idx + 1]
        vehiculo.posicion_anterior = vehiculo.posicion
        vehiculo.posicion = (nx, ny)
        self.ruta_idx[k] = idx + 1
        return True

    def inicio_regreso_base(self, vehiculo):
        """
        Arma la ruta de regreso EXACTA por los mismos pasos (path_ida invertido).
        """
        k = self._veh_key(vehiculo)
        pi = self.path_ida.get(k, [])
        if not pi:
            return

        # asegurar que la pos actual quede al final del histórico
        if pi[-1] != vehiculo.posicion:
            pi = pi + [vehiculo.posicion]
            self.path_ida[k] = pi

        ruta_vuelta = list(reversed(pi))

        # alinear para que arranque en la pos actual
        if ruta_vuelta[0] != vehiculo.posicion:
            if vehiculo.posicion in ruta_vuelta:
                i = ruta_vuelta.index(vehiculo.posicion)
                ruta_vuelta = ruta_vuelta[i:]
            else:
                ruta_vuelta.insert(0, vehiculo.posicion)

        self.ruta_activa[k] = ruta_vuelta
        self.ruta_idx[k] = 0
        self.returning.add(k)

    def _step_regreso(self, vehiculo):
        """
        Consume un paso del regreso; si termina, entrega y resetea path_ida.
        """
        moved = self._step_ruta(vehiculo)
        k = self._veh_key(vehiculo)
        ruta = self.ruta_activa.get(k)
        idx = self.ruta_idx.get(k, 0)

        # ¿terminó la ruta de regreso?
        if not ruta or idx >= len(ruta) - 1:
            self.returning.discard(k)
            try:
                self.registrar_entrega(vehiculo)
            except Exception:
                pass
            # preparar para nueva salida (mantener base como primer nodo)
            self.path_ida[k] = [vehiculo.posicion]
        return moved

    #muy mucho importante
    def ejecutar_un_paso_simulacion(self):
        """
        Avanza la simulación un tick:
        - prioridad: regreso a base > seguir ruta activa > (nada)
        - auto-recolecta recurso si cae sobre uno
        - guarda frame en historial
        """
        print(f"🕹️ Paso de simulación {self.step_count} (estado: {self.sim_state})")

        # 1) mover vehículos
        for v in self.vehiculos:
            k = self._veh_key(v)
            if k in self.returning:
                self._step_regreso(v)
            elif self.tiene_ruta(v):
                self._step_ruta(v)

            # 2) si cayó sobre un recurso, lo toma y puede disparar regreso
            if v.posicion in self.pos_recursos:
                if v.agarrar_recurso(self):
                    # si querés que vuelva al llenar capacidad, chequealo acá
                    if len(v.carga_actual) >= v.capacidad_carga:
                        self.inicio_regreso_base(v)

            # 3) si está en base y trae carga (caso de llegada sin 'returning' marcado)
            col = v.posicion[1]
            if self.es_base(col) and v.carga_actual:
                self.registrar_entrega(v)

        # 4) refrescar y guardar frame
        self.actualizar_matriz()
        self.step_count = getattr(self, "step_count", 0) + 1
        self._guardar_estado_en_historial()
        self.indice_historial = len(self.historial_matrices) - 1

        # 5) cortar a los 60 pasos si querés
        if self.step_count >= 60:
            self.set_sim_state("stopped")
