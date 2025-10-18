from src.aircraft import *
from src.mines import *
from src.resources import *
from src.base import *
import random


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
                
                    nuevo_vehiculo = clase(posicion=(x, y), jugador=jugador)
                    base_actual.vehiculos.append(nuevo_vehiculo)
                    self.vehiculos.append(nuevo_vehiculo) 
        self.actualizar_matriz()

    
    def initialization_simulation(self):
        self.inicializar_elementos_aleatoriamente()
        self.inicializar_vehiculos()
        self.actualizar_matriz()
        self.mostrar_tablero()
     
         
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
                    
        # 4. Poner Vehículos (Debe ir último para que sobrescriba)
        for v in self.vehiculos:
            x, y = v.posicion
            if 0 <= x < self.largo and 0 <= y < self.ancho:
                 self.matriz[x][y] = v.tipo[0]

    def actualizar_matriz_parcial(self):
        for v in self.vehiculos:
            x_ant, y_ant = v.posicion_anterior
            self.matriz[x_ant][y_ant] = "0"
        for v in self.vehiculos:
            x, y = v.posicion
            self.matriz[x][y] = v.tipo[0]

    def mostrar_tablero(self):
        for fila in self.matriz:
            print(" ".join(f"[{celda}]" for celda in fila))


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

        