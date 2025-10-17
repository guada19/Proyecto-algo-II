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

        # --- cargar sprites ---
        self._cargar_sprites()

    def _cargar_sprites(self):
        self.img_cache = {}

        def load(name):
            ruta = os.path.join(os.path.dirname(__file__), "..", "data", "imagenes", name)
            if not os.path.exists(ruta):
                print(f"⚠️ Archivo no encontrado: {ruta}")
                return None
            try:
                # ahora sí: convert_alpha, ya hay display
                return pygame.image.load(ruta).convert_alpha()
            except Exception as e:
                print(f"⚠️ No se pudo cargar {name}: {e} ({ruta})")
                return None

        self.img_cache["J"] = load("jeep.png")
        self.img_cache["M"] = load("moto.png")
        self.img_cache["C"] = load("camion.png")
        self.img_cache["A"] = load("auto.png")
        self.img_cache["r"] = load("ropa.png")
        self.img_cache["c"] = load("comida.png")
        self.img_cache["m"] = load("medicina.png")
        self.img_cache["PER"] = load("hombre.png")
        self.img_cache["a"] = load("armamento.png")


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
        pad = 3

        # ---------- VEHÍCULOS (ahora con imagen) ----------
        img = self.img_cache.get(tipo)
        if img:  # si hay sprite cargado para J/M/C/A
            iw, ih = img.get_size()

            # tamaño máximo disponible (respetando padding)
            max_w = max(1, rect.width  - 2*pad)
            max_h = max(1, rect.height - 2*pad)

            # factor de escala que NO deforma
            s = min(max_w / iw, max_h / ih)
            new_w = max(1, int(iw * s))
            new_h = max(1, int(ih * s))

            sprite = pygame.transform.smoothscale(img, (new_w, new_h))

            # centrar dentro de la celda
            x = rect.centerx - new_w // 2
            y = rect.centery - new_h // 2
            self.pantalla.blit(sprite, (x, y))
            return  
            
        # ---------- MINAS ----------
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

        # ---------- RECURSOS (con imagenes (las que hay)) Y fallback ----------
        if tipo in self.img_cache and self.img_cache[tipo]:
            img = self.img_cache[tipo]
            iw, ih = img.get_size()
            pad = 3
            max_w = rect.width - 2*pad
            max_h = rect.height - 2*pad
            s = min(max_w / iw, max_h / ih)
            new_w = int(iw * s)
            new_h = int(ih * s)
            sprite = pygame.transform.smoothscale(img, (new_w, new_h))
            x = rect.centerx - new_w // 2
            y = rect.centery - new_h // 2
            self.pantalla.blit(sprite, (x, y))
            return
        
        color = {
            #"J": (164, 179,  53),   # Jeep
            #"M": (246, 154,  84),   # Moto
            #"C": (243,  92,  72),   # Camión
            #"A": (255, 240, 130),   # Auto
            "PER": (204, 153, 179), # Persona
            "m": (204, 178, 153),   # Medicamento
            "a": (179, 204, 153),   # Armamento
            "c": (204, 153, 179),   # comida
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
    