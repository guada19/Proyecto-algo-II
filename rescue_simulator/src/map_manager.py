from src.aircraft import *
from src.mines import *
from src.resources import *
from src.base import *
from config.strategies.player1_strategies import Estrategia_J1
from config.strategies.player2_strategies import Estrategia_J2
import random
import copy
import math


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
        self.colisiones_visible = set()    # Colisiones que están visibles en el historial
        self.colisiones_just_added = set()

        # contador de pasos de simulación 
        self.step_count = 0


        
    
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
        Vehiculo.filas_por_jugador = {1: 2, 2: 2}

        for clase, cantidad in tipos:
            for jugador in (1, 2):
                base_actual = self.bases[jugador]
                for _ in range(cantidad):
                    if jugador == 1:
                        x = Vehiculo.filas_por_jugador[1]
                        y = 0
                        Vehiculo.filas_por_jugador[1] += 3
                    else:
                        x = Vehiculo.filas_por_jugador[2]
                        y = self.ancho-1
                        Vehiculo.filas_por_jugador[2] += 3
                
                    nuevo_vehiculo = clase(posicion=(x, y), jugador=jugador)
                    base_actual.vehiculos.append(nuevo_vehiculo)
                    self.vehiculos.append(nuevo_vehiculo) 
        
        estrategia_j1 = Estrategia_J1(self.bases[1].jugador, self.bases[1], self) 
        estrategia_j2 = Estrategia_J2(self.bases[2].jugador, self.bases[2], self) 

        for vehiculo in self.vehiculos:
            if vehiculo.jugador == 1:
                vehiculo.estrategia = estrategia_j1
                continue
                #print(f"Esta es la estrategia de los vehiculos: {vehiculo.estrategia}")
            elif vehiculo.jugador == 2:
                vehiculo.estrategia = estrategia_j2
        
        self.actualizar_matriz()
    
    def colision_minas(self, pos_x, pos_y):
        """
        Verifica si la posición (pos_x, pos_y) está dentro del radio de efecto de CUALQUIER mina activa.
        Esta función es usada por el motor del juego y el A* para EVITAR la zona.
        """
        if pos_y == 0 or pos_y == self.ancho - 1:
            return False
        
        for mine in self.minas:
            if mine.estado != "activa":
                continue

            mx, my = mine.posicion
            radio = mine.radio 
            
            if mine.tipo in ["01", "02", "G1"]: 
                distance = math.sqrt((pos_x - mx)**2 + (pos_y - my)**2)
                if distance <= radio:
                    if (pos_y == 0 or pos_y == self.ancho - 1):
                        continue
                    return mine
                
            elif mine.tipo == "T1": 
                if pos_x == mx and abs(pos_y - my) <= radio:
                    return mine

            elif mine.tipo == "T2": 
                if pos_y == my and abs(pos_x - mx) <= radio:
                    if pos_y == 0 or pos_y == self.ancho - 1:
                        continue
                    return mine

        return None

    def colision_vehiculos(self, vehicles_to_destroy):
        """
        Detecta colisiones por superposición de 'posicion_intencionada' 
        y añade los vehículos involucrados al set de destrucción.
        """
        intended_positions = {} 

        for vehiculo in self.vehiculos:
            if vehiculo.estado == "activo" and vehiculo not in vehicles_to_destroy:
            
                pos = vehiculo.posicion_intencionada

                if self.es_base(pos[1]) is not None:
                    continue 

                if pos not in intended_positions:
                    intended_positions[pos] = []

                intended_positions[pos].append(vehiculo)

        for pos, competing_vehicles in intended_positions.items():
            if len(competing_vehicles) > 1:
                for vehiculo in competing_vehicles:
                    vehicles_to_destroy.add(vehiculo)

        return vehicles_to_destroy

    
    def detectar_y_ejecutar_fallas(self):
        """
        Paso 4: Detecta colisiones basadas en la posición intencionada y ejecuta la destrucción.
        """
        vehicles_to_destroy = set()
        
        for vehiculo in self.vehiculos:
            if vehiculo.estado == "activo":
                x_int, y_int = vehiculo.posicion_intencionada
                
                mina_colisionada = self.colision_minas(x_int, y_int)
                if mina_colisionada:
                    vehicles_to_destroy.add(vehiculo)
                    mina_colisionada.explotar()
                    
        vehicles_to_destroy = self.colision_vehiculos(vehicles_to_destroy) 

        for vehiculo in vehicles_to_destroy:
            vehiculo.destruir() 
     

    def initialization_simulation(self):
        self.step_count = 0
        self.inicializar_elementos_aleatoriamente()
        self.inicializar_vehiculos()
        self.actualizar_matriz()
        #self.mostrar_tablero()
        
    def update_mobile_elements(self):
        """Llama a la lógica de movimiento y estado de elementos dinámicos (ej. Mina G1)."""
        
        for m in self.minas:
            if m.tipo == "G1":
                m.actualizar_estado(self.step_count, self)
                
    def ejecutar_un_paso_simulacion(self):
        """
        Ejecuta todas las acciones que ocurren en una única instancia de tiempo (tick).
        Llamada una vez por cada "segundo" de simulación por el bucle principal de Pygame.
        """
        
        if self.sim_state != "running":
            return
            
        self.step_count += 1
 
        self.update_mobile_elements() 
        
        for vehiculo in self.vehiculos:
            if vehiculo.estado == "activo" and vehiculo.estrategia:
                
                proximo_paso = vehiculo.estrategia.obtener_siguiente_paso(vehiculo) 
                
                if proximo_paso:
                    vehiculo.posicion_intencionada = proximo_paso
                else:
                    vehiculo.posicion_intencionada = vehiculo.posicion 
            
            elif vehiculo.estado != "activo":
                
                vehiculo.posicion_intencionada = (-1, -1)
        
        self.detectar_y_ejecutar_fallas() 
        
        for vehiculo in self.vehiculos:
            if vehiculo.estado == "activo":
                vehiculo.mover(vehiculo.posicion_intencionada)
                
                self.registrar_entrega(vehiculo) 
                vehiculo.agarrar_recurso(self) 
        
        
        self.actualizar_matriz() 
        self._guardar_estado_en_historial()
        
        if self.step_count >= 60:
            self.set_sim_state("stopped")
    
    def colision_vehiculos_para_a_star(self, x, y):
        """
        Retorna True si la celda (x, y) está ocupada actualmente o va a estar ocupada en el próximo tick.
        Evita que A* planifique caminos que causen colisiones.
        """
        if y == 0 or y == self.ancho-1:
            return False
        
        for v in self.vehiculos:
            if v.estado != "activo":
                continue
            # ocupa la celda actual o la intencionada
            if v.posicion == (x, y) or v.posicion_intencionada == (x, y):
                return True
        return False
    
    def definir_ganador(self):
        ganador = None
        if self.puntaje["J1"] > self.puntaje["J2"]:
            ganador = "Jugador 1"
        elif self.puntaje["J2"] > self.puntaje["J1"]:
            ganador = "Jugador 2"
        return ganador
    
    def start_simulation(self):
        #Acá es donde cada jugador debería ejecutar su propia estrategia
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
                    self.matriz[x][y] = 'PER' if r.categoria == "persona" else r.subtipo[0] 
                    self.matriz[x][y] = 'PER' if r.categoria == "persona" else r.subtipo[0] 
                    
        # 4. Poner Vehículos (Debe ir último para que sobrescriba)
        for v in self.vehiculos:
            x, y = v.posicion
            if 0 <= x < self.largo and 0 <= y < self.ancho:
                 self.matriz[x][y] = v.tipo[0]

    #función para saber si la columna del tablero es base
    def es_base(self, col):
        if col == 0:
            return "1"
        if col == self.ancho - 1:
            return "2"
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
                key = subtipo.lower()
                if key == "comida":
                    key = "alimento"
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
        
        base_label = "J1" if base == "1" else "J2"
        veh_label  = "J1" if vehiculo.jugador == 1 else "J2"

        if veh_label != base_label:
            return

        if not vehiculo.carga_actual:
            return  # No tiene carga

        total = 0
        for item in vehiculo.carga_actual:
            total += self.puntos_por(item)

        self.puntaje[base_label] += total
        self.entregas[base_label] += len(vehiculo.carga_actual)

        vehiculo.limpiar_carga()
        print(f"{base_label} entregó carga (+{total} pts). Total: {self.puntaje[base_label]}")
        
        # Decrementar viajes SOLO al entregar en base propia
        try:
            if vehiculo.viajes_restantes is None:
                vehiculo.viajes_restantes = vehiculo.max_viajes
        except Exception:
            # fallback defensivo
            vehiculo.viajes_restantes = getattr(vehiculo, "viajes_restantes", vehiculo.max_viajes)

        vehiculo.viajes_restantes -= 1

        if vehiculo.viajes_restantes <= 0:
            # Sin viajes: retirar
            vehiculo.marcar_retirado()
        else:
            # Con viajes: queda listo en base para un nuevo viaje
            vehiculo.reiniciar_para_nuevo_viaje()
            # Asegurar que objetivos/ruta no arrastren estado anterior
            vehiculo.camino_restante = []
            vehiculo.objetivo_recurso = None
            vehiculo.posicion_intencionada = vehiculo.posicion
        
        self.actualizar_matriz()
        try:
            self._guardar_estado_en_historial()
            self.indice_historial = len(self.historial_matrices) - 1
        except Exception:
            pass

    def copiar_estado_de(self, otro_tablero):
        """Copia de forma segura las estructuras principales desde otro tablero."""
        # Deepcopy asegura que no compartan referencias
        self.matriz = copy.deepcopy(getattr(otro_tablero, "matriz", []))
        self.vehiculos = copy.deepcopy(getattr(otro_tablero, "vehiculos", []))
        self.minas = copy.deepcopy(getattr(otro_tablero, "minas", []))
        self.recursos = copy.deepcopy(getattr(otro_tablero, "recursos", []))
        self.historial = copy.deepcopy(getattr(otro_tablero, "historial", []))
        
        # Estado de simulación
        self.sim_state = getattr(otro_tablero, "sim_state", "running")

#---Funciones que se quedan ---

    # --- Métodos de Control de la Simulación ---
    def set_sim_state(self, new_state):
        #"""Establece el estado de la simulación y realiza acciones de inicio/parada."""
        if new_state == "init":
             # Inicializa la simulación (poblar elementos) y quitar overlay de "juego finalizado"
             self.game_finished = False
             self.puntaje = {"J1": 0, "J2": 0}
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
            self.historial_matrices = [copy.deepcopy(self.matriz)]
            self.indice_historial = 0
            # activar overlay de "juego finalizado"
            self.game_finished = True
        else:
            self.sim_state = new_state
            
    def toggle_sim_state(self):
        #"""Alterna entre running y paused."""
        if self.sim_state == "running":
            self.sim_state = "paused"
        elif self.sim_state == "paused":
            vehiculos_sin_estrategia = [v for v in self.vehiculos if not getattr(v, "estrategia", None)]
            if vehiculos_sin_estrategia:
                print("❌ No se puede iniciar la simulación: algunos vehículos no tienen estrategia asignada.")
                for v in vehiculos_sin_estrategia:
                    print(f"   → {v.tipo} del jugador {v.jugador} sin estrategia")
                self.sim_state = "paused"
                return        
            self.sim_state = "running"
        elif self.sim_state == "init": # Si se presiona antes de que inicie la simulación
            self.initialization_simulation()
            self.sim_state = "paused"
        
    def _guardar_estado_en_historial(self):
        #"""Guarda la matriz actual como una nueva entrada en el historial."""
        # Si estamos "atrás" en el historial, borramos el futuro antes de añadir uno nuevo
        if self.indice_historial < len(self.historial_matrices) - 1:
            self.historial_matrices = self.historial_matrices[:self.indice_historial + 1]

        # Construir frame con overlays (copias, para que el historial sea inmutable)
        frame = {
            "matriz": copy.deepcopy(self.matriz),
            # ESTAS LÍNEAS YA NO DEBERÍAN CAUSAR ERROR:
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
        #"""Retorna el frame completo (matriz + overlays) correspondiente al índice actual."""
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
        #""""""Compatibilidad: retorna solo la matriz del frame actual (método usado anteriormente).""""""
        frame = self.obtener_frame_actual()
        return frame.get("matriz", self.matriz)

    def prev_frame(self):
        #"""Retrocede un paso en el historial (Botón <<)."""
        if self.indice_historial > 0:
            self.indice_historial -= 1
            # Forzar la pausa al moverse en el historial
            if self.sim_state == "running":
                self.sim_state = "paused"

    def next_frame(self):
        
        #"""Avanza un paso en el historial (Botón >>)."""
        if self.indice_historial < len(self.historial_matrices) - 1:
            self.indice_historial += 1
            # Forzar la pausa al moverse en el historial
            if self.sim_state == "running":
                self.sim_state = "paused"
        elif self.sim_state == "running":
             # Si estamos al final y la simulación está corriendo, realiza el siguiente paso
             self.ejecutar_un_paso_simulacion()