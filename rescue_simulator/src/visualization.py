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
    def __init__(self, tablero, ancho=1100, alto=900):
        
        # Colores base
        self.color_fondo = (78, 77, 52)    #fondo general
        self.color_grid_line = (60, 54, 49)  #lineas
        self.color_panel = (143, 125, 110)    # bases
        self.color_grid_bg = (149, 135, 122)  #fondo tablero
        self.color_borde = (57, 50, 44)      # bordes negros
        self.color_titulo = (210, 180, 140)  #titulos
        #fuentes 
        self.font_titulo = pygame.font.Font(font_1, 35)
        self.font_bases = pygame.font.Font(font_2, 18)
        self.font_timer = pygame.font.Font(font_2, 16)
        
        # --- títulos y header ---
        self.title = "Rescue Simulator"   # nombre
        self.header_pad = 8          # relleno interno del header
        self.header_gap = 10         # separación entre header y tablero
        
        h_title = self.font_titulo.get_height()
        h_timer = self.font_timer.get_height()

        self.header_h = max(70, h_title + 4 + h_timer + 2*self.header_pad)

        #---- botones y footer ----
        self.footer_h   = 35        # alto del pie donde irán los botones
        self.footer_gap = 20        # separación entre tablero y footer


        self.timer_seconds = 0
        self.tablero = tablero
        self.ancho = ancho
        self.alto = alto

        pygame.init()
        pygame.font.init()
        self.pantalla = pygame.display.set_mode((self.ancho, self.alto))
        pygame.display.set_caption("Simulador - Tablero")
        self.clock = pygame.time.Clock()


        self._compute_layout(margen = 40)
        self._build_buttons()
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

        #Vehiculos
        self.img_cache["J"] = load("jeep2.png")
        self.img_cache["M"] = load("moto2.png")
        self.img_cache["C"] = load("camion2.png") #Momentaneo, pequeña discusion con gpt
        self.img_cache["A"] = load("auto2.png")
        #Recursos
        self.img_cache["r"] = load("ropa.png")
        self.img_cache["c"] = load("comida.png")
        self.img_cache["m"] = load("medicina.png")
        self.img_cache["PER"] = load("persona.png")
        self.img_cache["a"] = load("armamento.png")
        #Minas
        self.img_cache["01"] = load("minaO1.png")
        self.img_cache["02"] = load("minaO2.png")
        self.img_cache["T1"] = load("minaT1.png")
        self.img_cache["T2"] = load("minaT2.png")
        self.img_cache["G1"] = load("minaG1.png")

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
        """Reserva header arriba, footer abajo, paneles laterales y centra la grilla."""
        self.columnas = int(self.tablero.ancho)
        self.filas    = int(self.tablero.largo)

        self.base_w = int(base_px)
        self.margen = int(margen)

        # área útil (dentro de márgenes + header + footer)
        avail_w = self.ancho - 2*self.margen
        avail_h = (self.alto
                - 2*self.margen
                - self.header_h
                - self.header_gap
                - self.footer_h
                - self.footer_gap)

        central_cols = max(self.columnas - 2, 1)
        central_avail_w = max(avail_w - 2*self.base_w, 1)

        # tamaño de celda y dimensiones
        self.celda = max(6, min(central_avail_w // central_cols, avail_h // self.filas))
        self.central_w = self.celda * central_cols
        self.central_h = self.celda * self.filas

        # origen X para centrar (panel izq + grilla + panel der)
        total_w = self.base_w*2 + self.central_w
        self.gx = (self.ancho - total_w) // 2

        # origen Y del tablero: debajo del header
        self.gy = self.margen + self.header_h + self.header_gap

        # rects útiles para dibujar
        self.base1_rect = pygame.Rect(self.gx, self.gy, self.base_w, self.central_h)
        self.central_rect = pygame.Rect(self.gx + self.base_w, self.gy, self.central_w, self.central_h)
        self.base2_rect = pygame.Rect(self.central_rect.right, self.gy, self.base_w, self.central_h)

        # footer centrado debajo del tablero
        fy = self.gy + self.central_h + self.footer_gap
        self.footer_rect = pygame.Rect(self.margen, fy, self.ancho - 2*self.margen, self.footer_h)

    #Botones
    def _build_buttons(self):
        etiquetas = [("Init", "init"), ("Play/Pause", "play"), ("Replay", "replay")]
        n = len(etiquetas)
        btn_w, btn_h, gap = 160, 40, 16

        total_w = n*btn_w + (n-1)*gap
        start_x = self.central_rect.centerx - total_w // 2  # centrado respecto al TABLERO
        y = self.footer_rect.centery - btn_h // 2

        self.buttons = []
        for i, (text, key) in enumerate(etiquetas):
            x = start_x + i*(btn_w + gap)
            rect = pygame.Rect(x, y, btn_w, btn_h)
            self.buttons.append({"rect": rect, "text": text, "key": key})

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

        # título y reloj centrados
        title_surf = self.font_titulo.render(self.title, True, self.color_titulo)
        timer_surf = self.font_timer.render(self._format_time(self.timer_seconds), True, self.color_titulo)
        
        total_height = title_surf.get_height() + 4 + timer_surf.get_height()
        top_y = header_rect[1] + (header_rect[3] - total_height) // 2

        title_x = header_rect[0] + (header_rect[2] - title_surf.get_width()) // 2
        self.pantalla.blit(title_surf, (title_x, top_y))

        timer_x = header_rect[0] + (header_rect[2] - timer_surf.get_width()) // 2
        self.pantalla.blit(timer_surf, (timer_x, top_y + title_surf.get_height() + 4))

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

        # Puntajes (izq/dcha) — toman self.tablero.puntaje
        p1 = self.tablero.puntaje.get("J1", 0)
        p2 = self.tablero.puntaje.get("J2", 0)
        p1_surf = self.font_bases.render(f"J1: {p1}", True, self.color_titulo)
        p2_surf = self.font_bases.render(f"J2: {p2}", True, self.color_titulo)

        padx = 12
        py = header_rect[1] + (header_rect[3] - p1_surf.get_height()) // 2
        self.pantalla.blit(p1_surf, (header_rect[0] + padx, py))
        self.pantalla.blit(p2_surf, (header_rect[0] + header_rect[2] - padx - p2_surf.get_width(), py))

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

        # ----- FOOTER (barra) -----
        pygame.draw.rect(self.pantalla, self.color_fondo, self.footer_rect, border_radius=6)
        pygame.draw.rect(self.pantalla, self.color_fondo, self.footer_rect, 2, border_radius=6)

        # mouse para hover
        mx, my = pygame.mouse.get_pos()

        for b in self.buttons:
            r = b["rect"]
            hover = r.collidepoint((mx, my))
            pygame.draw.rect(self.pantalla, self.color_panel, r, border_radius=8)
            pygame.draw.rect(self.pantalla, self.color_grid_line, r, 2, border_radius=8)

            txt = self.font_bases.render(b["text"], True, self.color_titulo)
            tx = r.centerx - txt.get_width() // 2
            ty = r.centery - txt.get_height() // 2
            self.pantalla.blit(txt, (tx, ty))

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
    
        base_h = rect.height
        radio  = max(5, int(base_h * 0.45))
        lado   = max(6, int(base_h * 0.90))
        pad = 2

        # FACTORES DE ESCALA 
        escala_vehiculo = 2
        escala_persona  = 1.7
        escala_recurso  = 1.2
        escala_mina = 1.5

        # ---------- VEHÍCULOS, PERSONAS, RECURSOS, MINAS (con imagen) ----------
        img = self.img_cache.get(tipo)
        if img:
            iw, ih = img.get_size()

            # Elegir factor según tipo
            if tipo in ("J", "M", "C", "A"):
                escala = escala_vehiculo
            elif tipo.startswith("PER"):
                escala = escala_persona
            elif tipo in ("O1", "O2", "T1", "T2", "G1"):
                escala = escala_mina
            else:
                escala = escala_recurso

            # tamaño máximo disponible dentro de la celda
            max_w = rect.width
            max_h = rect.height
            s = min((max_w * escala) / iw, (max_h * escala) / ih)

            new_w = int(iw * s)
            new_h = int(ih * s)

            if new_w % 2: new_w -= 1
            if new_h % 2: new_h -= 1

            sprite = pygame.transform.smoothscale(img, (new_w, new_h))

            # centrar
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


    def draw_from_tablero(self):
        """Pinta todo lo no-vacío de tablero.matriz usando cell_to_rect(col,fila)."""
        for fila in range(self.filas):
            for col in range(self.columnas):
                celda = self.tablero.matriz[fila][col]
                if celda in ("0", 0, None, ""):
                    continue
                rect = self.cell_to_rect(col, fila, pad=4)
                self.draw_item(celda, rect)
    

    #Para cuando tengamos el tema reloj resuelto
    def set_timer(self, seconds:int|None):
        """Actualiza el número que se muestra en el HUD. None = no mostrar."""
        self.timer_seconds = seconds

    def _format_time(self, s:int) -> str:
        # 60 -> "01:00", 9 -> "00:09"
        m, ss = divmod(max(0, int(s)), 60)
        return f"{m:02d}:{ss:02d}"

