import pygame
pygame.init()


# Colores base
COLOR_FONDO = (78, 77, 52)
COLOR_LINEA = (60, 54, 49)
COLOR_BASE1 = (78, 77, 52)    # base izquierda (jugador 1)
COLOR_BASE2 = (78, 77, 52)    # base derecha (jugador 2)
COLOR_MAPA = (149, 135, 122)

#Clase que muestra todo en pantalla
class Visualizer:
    """
    Visualizador simple para el Tablero.
    - columnas = tablero.ancho, filas = tablero.largo
    - bases: col 0 (B1) y col columnas-1 (B2) dentro del tablero
    - colores por contenido de celda en draw_from_tablero()
    """
    #Inicializa el tablero
    def __init__(self, tablero, ancho=1000, alto=600):
        
        self.tablero = tablero
        self.ancho = ancho
        self.alto = alto

        pygame.init()
        self.pantalla = pygame.display.set_mode((self.ancho, self.alto))
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

            self.pantalla.fill((COLOR_FONDO))  # fondo liso por ahora
            self.draw_grid()
            #self.draw_from_tablero()


            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()

    #Calcula el tamaño de las celdas
    def _compute_layout(self, margen=40, base_px=140):
        """Reserva 'base_px' para cada base y ajusta la grilla central."""
        self.columnas = self.tablero.ancho
        self.filas    = self.tablero.largo

        mx = my = margen
        self.base_w = base_px

        # espacio disponible para TODO el tablero (bases + grilla)
        avail_w = self.ancho - 2*mx
        avail_h = self.alto  - 2*my

        # columnas de la grilla central (excluye 0 y cols-1)
        centro_columnas = max(self.columnas - 2, 0)

        # ancho disponible para la grilla central (restando bases)
        ancho_centro = max(avail_w - 2*self.base_w, 1)

        # tamaño de celda (todas las filas tienen la misma altura)
        celda_ancho = ancho_centro // max(centro_columnas, 1) if centro_columnas > 0 else ancho_centro
        celda_alto = avail_h // self.filas
        self.celda = max(8, min(celda_ancho, celda_alto))

        # dimensiones reales de cada zona
        self.central_w = self.celda * centro_columnas
        tablero_ancho = self.base_w*2 + self.central_w
        tablero_alto = self.celda * self.filas

        # origen para centrar todo el tablero
        self.gx = (self.ancho - tablero_ancho) // 2
        self.gy = (self.alto  - tablero_alto) // 2

    #Dibuja las cuadriculas del tablero
    def draw_grid(self):
        gx = self.gx
        gy = self.gy
        h = self.celda * self.filas

        # --- bases laterales (fuera de la grilla) ---
        # izquierda
        left_base_rect = (gx, gy, self.base_w, h)
        # derecha
        right_base_x = gx + self.base_w + self.central_w
        right_base_rect = (right_base_x, gy, self.base_w, h)

        # --- área central (grilla) ---
        central_x = gx + self.base_w
        central_rect = (central_x, gy, self.central_w, h)

        # fondos
        pygame.draw.rect(self.pantalla, COLOR_MAPA, central_rect)
        pygame.draw.rect(self.pantalla, COLOR_BASE1, left_base_rect)
        pygame.draw.rect(self.pantalla, COLOR_BASE2, right_base_rect)

        # líneas verticales SOLO en la grilla central
        central_cols = max(self.columnas - 2, 0)
        for c in range(central_cols + 1):
            x = central_x + c * self.celda
            pygame.draw.line(self.pantalla, COLOR_LINEA, (x, gy), (x, gy + h), 1)

        # horizontales (a lo ancho de toda el área, o solo central si preferís)
        # acá las hago solo sobre la grilla central para reforzar el efecto
        for r in range(self.filas + 1):
            y = gy + r * self.celda
            pygame.draw.line(self.pantalla, COLOR_LINEA, (central_x, y), (central_x + self.central_w, y), 1)   


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


    #Forma visual de los elementos (ES TEMPORAL, necesitamos que exista despues lo mejoramos)
    """def draw_from_tablero(self):
        colores = {
            "J": (255, 220, 70),   # Jeep
            "M": (255, 170, 70),   # Moto
            "C": (255, 255, 110),  # Camión
            "A": (255, 240, 130),  # Auto
            "R": (0, 200, 120),    # Recurso
            "X": (200, 0, 0),      # Mina
            "B1": (120, 40, 40),   # si querés marcar base en matriz
            "B2": (40, 40, 120),
        }
        for fila in range(self.filas):
            for col in range(self.columnas):
                celda = self.tablero.matriz[fila][col]
                if celda in ("0", 0, None, ""):
                    continue
                rect = self.cell_to_rect(col, fila)
                color = colores.get(celda, (160,160,160))
                pygame.draw.rect(self.pantalla, color, rect)"""



