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
        
        # Simulación y Historial
        # Estado: 'stopped', 'init', 'running', 'paused'
        self.sim_state = "stopped" 
        self.historial_matrices = [] 
        self.indice_historial = 0

        # Posiciones de colisión visibles SOLO durante el paso en que ocurren
        # (se almacena un set de tuplas (fila, col))
        self.colisiones_visible = set()

        # Flag para mostrar overlay de "juego finalizado" cuando se presiona STOP
        self.game_finished = False

        # Inicializamos las bases (usar atributos del objeto, no variables locales)
        self.base_jugador1 = Base(self.ancho, self.largo, 1, [])
        self.base_jugador2 = Base(self.ancho, self.largo, 2, [])
        self.bases = {1: self.base_jugador1, 2: self.base_jugador2}
        # Asegurar estado inicial vacío en la matriz e historial (sin elementos visibles)
        self.actualizar_matriz()
        self.historial_matrices = [copy.deepcopy(self.matriz)]
        self.indice_historial = 0    

    def add_collision(self, pos):
        """Registrar colisión en pos (fila, col) — se mantiene hasta el siguiente paso."""
        self.colisiones_visible.add(tuple(pos))

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
        # Se usa deepcopy para guardar una copia independiente de la matriz actual
        if self.indice_historial < len(self.historial_matrices) - 1:
            # Si estamos "atrás" en el historial, borramos el futuro antes de añadir uno nuevo
            self.historial_matrices = self.historial_matrices[:self.indice_historial + 1]
            
        self.historial_matrices.append(copy.deepcopy(self.matriz))
        self.indice_historial = len(self.historial_matrices) - 1

    def obtener_matriz_historial(self):
        """Retorna la matriz actual según el índice del historial."""
        if not self.historial_matrices:
            return self.matriz # Retorna la matriz actual si no hay historial
        return self.historial_matrices[self.indice_historial]

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
        """
        
        self.recursos = []
        self.minas = []
        self.pos_recursos = {}  
        self.pos_minas = {}
        self.posiciones_ocupadas = set() 
        
        elementos = self._crear_elementos()
        
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


        # Actualizar matriz
        self.actualizar_matriz()
        # Guardar el nuevo estado en el historial 
        self._guardar_estado_en_historial()
        # Se asegura de estar al final del historial
        self.indice_historial = len(self.historial_matrices) - 1

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