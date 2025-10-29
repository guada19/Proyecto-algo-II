En este archivo muestro los ficheros de python en el que `rescue_simulator.py` es el archivo principal del proyecto y el resto de los archivos de python estan en el directorio `src`.

rescue_simulator.py

```python
import pygame
from src.map_manager import Tablero
from src.visualization import Visualizer

def main():
    tablero = Tablero(ancho=20, largo=20)  # usa tus valores reales
    tablero.initialization_simulation()

    viz = Visualizer(tablero)
    
    # 3) loop de visualización
    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r:
                    # regenerar mapa: recursos/minas nuevas
                    tablero.inicializar_elementos_aleatoriamente()
                    tablero.actualizar_matriz()
                elif e.key == pygame.K_v:
                    # re-spawn de vehículos (opcional)
                    tablero.inicializar_vehiculos()
                    tablero.actualizar_matriz()

        # dibujar frame
        viz.pantalla.fill(viz.color_fondo)
        viz.draw_grid()
        viz.draw_from_tablero()   # ← pinta R/X/J/M/C/A según matriz
        pygame.display.flip()
        viz.clock.tick(60)

    pygame.quit()    

    wviz.run()
    
    
    

if __name__ == "__main__":
    main()


```

---

aircraft.py

```python
class Vehiculo:
    
    filas_por_jugador = {1: 0, 2: 0}
    
    def __init__(self, tipo, posicion, capacidad_carga, viajes_restantes, tipo_carga_permitida, estado, jugador, max_viajes):
        self.tipo = tipo
        self.x, self.y = posicion
        self.capacidad_carga = capacidad_carga
        self.viajes_restantes = viajes_restantes
        self.tipo_carga_permitida = tipo_carga_permitida
        self.estado = estado
        self.jugador = jugador
        self.max_viajes = max_viajes
        self.carga_actual = []
    
    @property
    def posicion(self):
        #retornar la posición como tupla
        return (self.x, self.y)
    
    def mover(self):
        pass
    
    def agarrar_recurso(self, tablero):
        
        recurso = tablero.pos_recursos.get(self.posicion)
        
        if recurso and recurso.estado == "disponible":
            if (recurso.categoria in self.tipo_carga_permitida) and len(self.carga_actual) < self.capacidad_carga:
                self.carga_actual.append(recurso)
                recurso.recolectado()
                self.viajes_restantes -= 1
                del tablero.pos_recursos[self.posicion]

                return True
        
        return False
            
    def volver_a_la_base(self):
        pass
    
    def detectar_colision(self):
        pass
    
    def destruir(self):
        #Marca el vehículo como destruido.
        self.estado = "destruido"

    def ejecutar_estrategia(self):
        #Acá habría que relacionarlo con la clase jugador accediendo a self.jugador
        #y que cada vehículo tenga su propio método con un @override
        if self.estado == "activo": 
            self.x += 1
            if self.y == 0:
                self.y +=1
            elif self.y == 15:
                self.y -= 1
    

class Jeep(Vehiculo):
    def __init__(self, posicion, jugador):
        super().__init__(tipo = "Jeep", posicion = posicion, capacidad_carga = 2, viajes_restantes = 2, tipo_carga_permitida = ["persona", "mercancia"], estado = "activo", jugador = jugador, max_viajes = 2)

class Moto(Vehiculo):
    def __init__(self, posicion,jugador):
        super().__init__(tipo = "Moto", posicion = posicion, capacidad_carga = 1, viajes_restantes = 1, tipo_carga_permitida = ["persona"], estado = "activo", jugador = jugador, max_viajes = 1)

class Camion(Vehiculo):
    def __init__(self, posicion, jugador):
        super().__init__(tipo = "Camion", posicion = posicion, capacidad_carga = 3, viajes_restantes = 3, tipo_carga_permitida = ["persona", "mercancia"], estado = "activo", jugador = jugador, max_viajes = 3)
   
class Auto(Vehiculo):
    def __init__(self, posicion, jugador):
        super().__init__(tipo = "Auto", posicion = posicion, capacidad_carga = 1, viajes_restantes = 1, tipo_carga_permitida = ["persona", "mercancia"], estado = "activo", jugador = jugador, max_viajes = 1) 
        
 
```

---

map_manager.py

```python
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

```

---

resources.py

```python
class Resource():
    def __init__(self, posicion, puntaje, estado, categoria):
        self.x, self.y = posicion
        self.puntaje = puntaje
        self.estado = estado 
        self.categoria = categoria
    
    def recolectado(self):
        self.estado = "recolectado"
     
    def destruirse(self):
        self.estado = "destruido"
        
class Person(Resource):
    def __init__(self):
        super().__init__(posicion = (0,0), puntaje = 50, estado = "disponible", categoria = "persona")


class Mercancia(Resource):
    def __init__(self, posicion, subtipo, puntaje):
        super().__init__(posicion = posicion, puntaje = puntaje, estado = "disponible", categoria = "mercancia")
        self.subtipo = subtipo 
        
class Alimento(Mercancia):
    def __init__(self):
        super().__init__(posicion = (0,0), subtipo = "alimento", puntaje = 10)

class Ropa(Mercancia):
    def __init__(self):
        super().__init__(posicion = (0,0), subtipo = "ropa", puntaje = 5)

class Medicamento(Mercancia):
    def __init__(self):
        super().__init__(posicion = (0,0), subtipo = "medicamento", puntaje = 20)

class Armamento(Mercancia):
    def __init__(self):
        super().__init__(posicion = (0,0), subtipo = "armamento", puntaje = 50)
```

---

base.py

```python
class Base():
    def __init__(self, ancho, largo, jugador, vehiculos):
        self.ancho = ancho
        self.largo = largo
        self.puntaje = 0
        self.jugador = jugador
        self.vehiculos = vehiculos
    
    def mostrar_puntaje(self):
        print(f"El puntaje del jugador: {self.jugador} es de: {self.puntaje}")
    
    def entregar_recursos(self, vehiculo):
        """Descarga los recursos del vehículo y suma los puntos."""
        pass
```

---

visualization.py

```python
import pygame
pygame.init()
import os

# ruta relativa al archivo actual
font_1 = os.path.join(os.path.dirname(__file__), "..", "data", "fonts", "RubikDirt-Regular.ttf")
font_2 = os.path.join(os.path.dirname(__file__), "..", "data", "fonts", "Galindo-Regular.ttf")
font_3 = os.path.join(os.path.dirname(__file__), "..", "data", "fonts", "Sixtyfour-Regular.ttf")

#Clase que muestra todo en pantalla
class Visualizer:
    """
    Visualizador simple para el Tablero.
    - columnas = tablero.ancho, filas = tablero.largo
    - bases: col 0 (B1) y col columnas-1 (B2) dentro del tablero
    - colores por contenido de celda en draw_from_tablero()
    """
    #Inicializa el tablero
    def __init__(self, tablero, ancho=1000, alto=700):
        
        # Colores base
        self.color_fondo = (78, 77, 52)    #fondo general
        self.color_grid_line = (60, 54, 49)  #lineas
        self.color_panel = (143, 125, 110)    # bases
        self.color_grid_bg = (149, 135, 122)  #fondo tablero
        self.color_borde = (57, 50, 44)      # bordes negros
        self.color_titulo = (210, 180, 140)  #titulos
        # --- títulos y header ---
        self.title = "Rescue Simulator"   # nombre
        self.header_h = 40                      # alto de la franja superior

        self.tablero = tablero
        self.ancho = ancho
        self.alto = alto

        pygame.init()
        pygame.font.init()
        self.pantalla = pygame.display.set_mode((self.ancho, self.alto))
        self.font_titulo = pygame.font.Font(font_1, 35)
        self.font_bases = pygame.font.Font(font_2, 18)
        pygame.display.set_caption("Simulador - Tablero")
        self.clock = pygame.time.Clock()


        self._compute_layout(margen = 40)

    #Bucle que mantiene el juego corriendo
    def run(self):
        corriendo = True
        while corriendo:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    corriendo = False

            self.pantalla.fill((self.color_fondo))  # fondo liso por ahora
            self.draw_grid()
            self.draw_from_tablero()


            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()

    def _compute_layout(self, margen=28, base_px=90):
        """Reserva paneles laterales (bases) y centra la grilla."""
        self.columnas = int(self.tablero.ancho)
        self.filas    = int(self.tablero.largo)

        self.base_w = int(base_px)
        self.margen = int(margen)

        # área total util (dentro del margen)
        avail_w = self.ancho - 2*self.margen
        avail_h = self.alto  - 2*self.margen - self.header_h

        # columnas solo del centro (excluye las de base lógicas)
        central_cols = max(self.columnas - 2, 1)

        # ancho disponible para la grilla central (resta paneles)
        central_avail_w = max(avail_w - 2*self.base_w, 1)

        # tamaño de celda y dimensiones
        self.celda = max(6, min(central_avail_w // central_cols, avail_h // self.filas))
        self.central_w = self.celda * central_cols
        self.central_h = self.celda * self.filas

        # origen para centrar todo (panel izq + grilla + panel der)
        total_w = self.base_w*2 + self.central_w
        self.gx = (self.ancho - total_w) // 2
        self.gy = self.margen + self.header_h + (avail_h - self.central_h) // 2

    #Dibuja las cuadriculas del tablero. Dibuja las bases también
    def draw_grid(self):
        gx = self.gx
        gy = self.gy
        h = self.central_h

        # rects
        base_j1   = (gx, gy, self.base_w, h) #Base jugador 1
        central_x    = gx + self.base_w
        central_rect = (central_x, gy, self.central_w, h)
        base_j2  = (central_x + self.central_w, gy, self.base_w, h) #Base jugador 2

        # ---------- HEADER ----------
        header_rect = (self.margen, self.margen, self.ancho - 2*self.margen, self.header_h)
        # fondo del header (opcional, podés usar self.color_fondo para transparente)
        pygame.draw.rect(self.pantalla, self.color_fondo, header_rect, 0, border_radius=4)
        pygame.draw.rect(self.pantalla, self.color_fondo, header_rect, 2, border_radius=4)

        # título centrado
        title_surf = self.font_titulo.render(self.title, True, self.color_titulo)
        title_x = header_rect[0] + (header_rect[2] - title_surf.get_width()) // 2
        title_y = header_rect[1] + (header_rect[3] - title_surf.get_height()) // 2
        self.pantalla.blit(title_surf, (title_x, title_y))

        # títulos “Base J1/J2”
        # etiquetas de bases, ubicadas en el header sobre cada panel
        base1_surf = self.font_bases.render("Base J1", True, self.color_titulo)
        base2_surf = self.font_bases.render("Base J2", True, self.color_titulo)

        # centro en X de cada panel lateral
        base1_cx = base_j1[0] + base_j1[2] // 2
        base2_cx = base_j2[0] + base_j2[2] // 2
        base_text_y = header_rect[1] + (header_rect[3] - base1_surf.get_height()) // 2    
        
        self.pantalla.blit(base1_surf, (base1_cx - base1_surf.get_width() // 2, base_text_y))
        self.pantalla.blit(base2_surf, (base2_cx - base2_surf.get_width() // 2, base_text_y))


        # paneles bases
        pygame.draw.rect(self.pantalla, self.color_panel, base_j1, 0, border_radius=2)
        pygame.draw.rect(self.pantalla, self.color_panel, base_j2, 0, border_radius=2)
        pygame.draw.rect(self.pantalla, self.color_borde, base_j1, 3, border_radius=2)
        pygame.draw.rect(self.pantalla, self.color_borde, base_j2, 3, border_radius=2)

        # área de grilla (fondo + borde)
        pygame.draw.rect(self.pantalla, self.color_grid_bg, central_rect, 0)
        
        # líneas de grilla (solo dentro del rect central)
        cols_centro = max(self.columnas - 2, 1)

        # Rectángulo interior donde van SOLO las líneas (dejamos margen del borde)
        inset = 1  # podés probar 2–4 px
        inner_left   = central_x + inset
        inner_top    = gy + inset
        inner_right  = central_x + self.central_w - inset
        inner_bottom = gy + h - inset
        inner_w = inner_right - inner_left
        inner_h = inner_bottom - inner_top

        # Verticales: de 1 a (cols_centro - 1) → NO dibujar las de los bordes
        for c in range(1, cols_centro):
            x = inner_left + c * (self.celda)
            pygame.draw.line(self.pantalla, self.color_grid_line, (x, inner_top), (x, inner_bottom), 2)

        # Horizontales: de 1 a (filas - 1) → NO dibujar las de los bordes
        for r in range(1, self.filas):
            y = inner_top + r * (self.celda)
            pygame.draw.line(self.pantalla, self.color_grid_line, (inner_left, y), (inner_right, y), 2)

        # --- borde del tablero (encima de las líneas) ---
        pygame.draw.rect(self.pantalla, self.color_borde, central_rect, 3)


    #permite que las bases sean consideradas dentro del tablero
    def cell_to_rect(self, col, fila, pad=2):
        """Devuelve el rect para una celda lógica (col,fila).
        col=0 → base izq, col=cols-1 → base der, resto → grilla central."""
        assert 0 <= col < self.columnas and 0 <= fila < self.filas

        y = self.gy + fila * self.celda
        h = self.celda

        if col == 0:
            x = self.gx
            w = self.base_w
        elif col == self.columnas - 1:
            x = self.gx + self.base_w + self.central_w
            w = self.base_w
        else:
            x = self.gx + self.base_w + (col - 1) * self.celda
            w = self.celda

        return pygame.Rect(x + pad, y + pad, max(1, w - 2*pad), max(1, h - 2*pad))

    # Forma visual TEMPORAL de los elementos
    def draw_item(self, tipo, rect):
        """Dibuja un item en 'rect' con formas simples:
        - R: círculo verde
        - X: cuadrado rojo
        - J/M/C/A: círculo de color por vehículo
        """
        base_h = rect.height
        radio  = max(5, int(base_h * 0.45))
        lado   = max(6, int(base_h * 0.90))

        if tipo in ("01", "02", "T1", "T2", "G1"):
            colores_mina = {
                "01": (121, 82, 39),      
                "02": (119, 40, 39),    
                "T1": (39, 118, 119),    
                "T2": (118, 119, 39),    
                "G1": (39, 78, 119),    
            }
            color = colores_mina.get(tipo, (200, 0, 0))
            r = pygame.Rect(rect.centerx - lado // 2,
                            rect.centery - lado // 2,
                            lado, lado)
            pygame.draw.rect(self.pantalla, color, r)
            pygame.draw.rect(self.pantalla, (25, 25, 25), r, 1)
            return

        color = {
            "J": (164, 179,  53),   # Jeep
            "M": (246, 154,  84),   # Moto
            "C": (243,  92,  72),   # Camión
            "A": (255, 240, 130),   # Auto
            "PER": (204, 153, 179), # Persona
            "m": (204, 178, 153),   # Medicamento
            "a": (179, 204, 153),   # Armamento
            "r": (153, 179, 204),   # ropa
        }.get(tipo, (160, 160, 160))

        pygame.draw.circle(self.pantalla, color, rect.center, radio)
        pygame.draw.circle(self.pantalla, (25, 25, 25), rect.center, radio, 1)  # borde fino


    def draw_from_tablero(self):
        """Pinta todo lo no-vacío de tablero.matriz usando cell_to_rect(col,fila)."""
        for fila in range(self.filas):
            for col in range(self.columnas):
                celda = self.tablero.matriz[fila][col]
                if celda in ("0", 0, None, ""):
                    continue
                rect = self.cell_to_rect(col, fila, pad=4)
                self.draw_item(celda, rect)
    
```

---

## Estructura de Archivos sugerida 

```bash
rescue_simulator/
├── rescue_simulator.py        # Archivo principal
├── config/
│ ├── default_config.json      # Configuración por defecto
│ └── strategies/
│   ├── player1_strategies.py      # Estrategias del jugador 1
│   └── player2_strategies.py      # Estrategias del jugador 2
├── src/
│ ├── game_engine.py           # Motor del juego
│ ├── aircraft.py              # Clases de aeronaves
│ ├── map_manager.py           # Gestión del mapa
│ ├── pathfinding.py           # Algoritmos de navegación
│ └── visualization.py         # Interfaz gráfica
├── data/
│ ├── simulations/             # Simulaciones guardadas
│ └── statistics/              # Estadísticas y análisis
└── tests/
  ├── test_aircraft.py           # Pruebas unitarias
  ├── test_pathfinding.py
  └── test_game_engine.py
```

Antes de iniciar cada juego o partida, se muestra el mapa con los recurso y minas , distribuidos al azar en el mapa. Los vehiculos se muestran todos en su base correspondiente.

Cada jugador dispone de una flota de diez vehículos distribuidos de la siguiente manera:
    - tres Jeeps,
    - dos Motos, 
    - dos Camiones,
    - tres Autos.

1. donde sea necesario, crear botones correspondientes para que se vea en el juego y su logica correspondiente en el lugar adecuado de la estructura del proyecto. El texto debe leerse dentro cada boton correspondiente.
2. el juego se inicia al presionar un boton `init`. Una vez presionado este boton, ya no puede volver a presionarse hasta que el juego termina. 
8. Al presionar el boton `stop`, el juego debe detenerse y no puede retomarse, es decir, el juego termina.
3. inmediatamente luego de ser presionado el boton `init`, un vehiculo sale de la base, a la posicion mas cercana en el mapa.
4. luego de cada movimiento debe registrarse el nuevo estado del mapa en alguna parte del proyecto para que pueda mostrar el paso a paso.
5. una vez que el vehiculo ha salido de la base, el vehiculo se mueve aleatoreamente en cada movimiento, pero no puede volver a la base.
6. entre cada movimiento hay un tiempo de 2 segundos.
7. Al presionar el boton `pause`, el juego debe quedar en pausa y al presionar otra vez `stop`, el juego vuelve a retomarse.
9. Al presionar el boton `<<`, se debe mostrar el frame inmediato anterior.
10. Al presionar el boton `>>` se debe mostrar el frame inmediato anterior.

cada archivo que modifiques, pasamelos completos para copiarlos

Teniendo en cuenta esta informacion, hacer un programa que maneje las coliciones entre vehiculos entre si, de tal modo que si dos vehiculos colisionan entre si, esos vehiculos involucrados asi como los recursos que esos vehiculos tengan cargados deben desaparecer del mapa y no vuelvan a ser cargados al mapa en lo que quede del juego.
