import pygame
pygame.init()
import os

# ruta relativa al archivo actual
font_1 = os.path.join(os.path.dirname(__file__), "..", "data", "fonts", "RubikDirt-Regular.ttf")
font_2 = os.path.join(os.path.dirname(__file__), "..", "data", "fonts", "Galindo-Regular.ttf")
font_3 = os.path.join(os.path.dirname(__file__), "..", "data", "fonts", "Sixtyfour-Regular.ttf")


#Clase que muestra todo en pantalla
class Visualizer:

    """Visualizador simple para el Tablero.
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

        self.clock = pygame.time.Clock()


        self._compute_layout(margen = 40, target_cell_px=48)

        self.pantalla = pygame.display.set_mode((self.ancho, self.alto))
        pygame.display.set_caption("Simulador - Tablero")

        self._cargar_sprites()
        self._build_buttons()

    def handle_button_click(self, e):
        """Procesa el clic del mouse y llama a la acción correspondiente."""
        for b in self.buttons:
            if b["enabled"] and b["rect"].collidepoint(e.pos):
                self._on_button(b["key"])
                break
    
    def _cargar_sprites(self):
        self.img_cache = {}

        def load(name):
            ruta = os.path.join(os.path.dirname(__file__), "..", "data", "imagenes", name)
            if not os.path.exists(ruta):
                print(f"Archivo no encontrado: {ruta}")
                return None
            try:
                # ahora sí: convert_alpha, ya hay display
                return pygame.image.load(ruta).convert_alpha()
            except Exception as e:
                print(f"No se pudo cargar {name}: {e} ({ruta})")
                return None

        #Vehiculos
        self.img_cache["J"] = load("jeep2.png")
        self.img_cache["M"] = load("moto2.png")
        self.img_cache["C"] = load("camion2.png") 
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

                elif e.type == pygame.MOUSEBUTTONUP and e.button == 1:
                    for b in self.buttons:
                        if b["enabled"] and b["rect"].collidepoint(e.pos):
                            self._on_button(b["key"])
                            break

                elif e.type == pygame.KEYDOWN:
                    if   e.key in (pygame.K_i, pygame.K_I): self._on_button("init")
                    elif e.key == pygame.K_SPACE:           self._on_button("play")
                    elif e.key in (pygame.K_s, pygame.K_S): self._on_button("stop")
                    elif e.key == pygame.K_LEFT:            self._on_button("prev")
                    elif e.key == pygame.K_RIGHT:           self._on_button("next")

            estado = getattr(self.tablero, "sim_state", None)
            if estado == "running":
                self.tablero.next_frame()
            elif estado == "paused":
                # no avanzar simulación
                pass

            self.pantalla.fill((self.color_fondo))  # fondo liso por ahora
            self.draw_grid()
            self.draw_from_tablero()
            self.draw_buttons()

            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()

    def _compute_layout(self, margen=28, base_px=90, target_cell_px=44):

        #Calcula layout centrado y agranda todo automáticamente,
        #sin exceder el tamaño de pantalla (cap a 95% ancho / 92% alto).

        self.columnas = int(self.tablero.ancho)
        self.filas    = int(self.tablero.largo)

        # Márgenes y tamaños base
        self.margen   = int(margen)
        self.base_w   = int(base_px)
        self.header_gap = getattr(self, "header_gap", 10)
        self.footer_gap = getattr(self, "footer_gap", 20)
        self.footer_h   = getattr(self, "footer_h", 35)

        # 1) Límite físico de pantalla (cap)
        info = pygame.display.Info()
        cap_w = int(info.current_w * 0.98)   # 95% del monitor
        cap_h = int(info.current_h * 0.96)   # 92% del monitor

        # 2) Intento con celda objetivo
        central_cols = max(self.columnas - 2, 1)

        cell = int(max(6, target_cell_px))
        base_w = int(self.base_w)

        def recompute_sizes(cell_px: int, base_w_px: int):
            # dimensiones de la grilla central
            central_w = cell_px * central_cols
            central_h = cell_px * self.filas
            total_w   = base_w_px*2 + central_w
            total_h   = (self.margen + self.header_h + self.header_gap +
                        central_h + self.footer_gap + self.footer_h + self.margen)
            # ancho total con márgenes
            window_w  = total_w + 2*self.margen
            window_h  = total_h
            return window_w, window_h, central_w, central_h

        window_w, window_h, central_w, central_h = recompute_sizes(cell, base_w)

        # 3) Si se excede, reducimos celda gradualmente; si no alcanza, también base_w
        min_cell = 10
        min_base = 80

        while (window_w > cap_w or window_h > cap_h) and (cell > min_cell or base_w > min_base):
            if cell > min_cell:
                cell = max(min_cell, int(cell * 0.9))  # baja 10% la celda
            elif base_w > min_base:
                base_w = max(min_base, int(base_w * 0.95))  # reducimos más suave
            window_w, window_h, central_w, central_h = recompute_sizes(cell, base_w)

        # 4) Ahora ajustamos self.ancho / self.alto a lo que realmente vamos a usar
        #    (pero nunca más grande que el cap)
        self.ancho = min(window_w, cap_w)
        self.alto  = min(window_h, cap_h)

        # 5) Recalcular centrado con estos tamaños finales (usa cell/base_w definitivos)
        self.celda      = cell
        self.base_w     = base_w
        avail_w = self.ancho - 2*self.margen
        # El alto ya está contenido por el cap; el tablero va centrado vertical entre header y footer,
        # así que no necesitamos "avail_h" para la celda (ya la definimos).
        self.central_w  = central_w
        self.central_h  = central_h

        total_w = self.base_w*2 + self.central_w
        self.gx = (self.ancho - total_w) // 2

        # centrar verticalmente el bloque tablero entre header y footer
        espacio_tablero = (self.alto - 2*self.margen - self.header_h - self.footer_h - self.footer_gap)
        offset_central  = max(0, (espacio_tablero - self.central_h) // 2)
        self.gy = self.margen + self.header_h + offset_central

        # rectángulos
        self.base1_rect   = pygame.Rect(self.gx, self.gy, self.base_w, self.central_h)
        self.central_rect = pygame.Rect(self.gx + self.base_w, self.gy, self.central_w, self.central_h)
        self.base2_rect   = pygame.Rect(self.central_rect.right, self.gy, self.base_w, self.central_h)

        fy = self.gy + self.central_h + self.footer_gap
        self.footer_rect = pygame.Rect(self.margen, fy, self.ancho - 2*self.margen, self.footer_h)

    #Botones
    def _build_buttons(self):
        etiquetas = [
            ("init", "init"),
            ("play", "play"),
            ("stop", "stop"),
            ("prev", "prev"),
            ("next", "next"),
        ]

        n = len(etiquetas)
        btn_w, btn_h, gap = 130, 50, 12
        total_w = n * btn_w + (n - 1) * gap
        start_x = self.footer_rect.centerx - total_w // 2
        y = self.footer_rect.centery - btn_h // 2

        self.buttons = []
        for i, (text, key) in enumerate(etiquetas):
            x = start_x + i * (btn_w + gap)
            rect = pygame.Rect(x, y, btn_w, btn_h)
            self.buttons.append({
                "rect": rect,
                "text": text,
                "key": key,
                "enabled": True,
            })

        self._set_enabled("init", True)
        self._set_enabled("play", False)
        self._set_enabled("stop", False)
        self._set_enabled("prev", False)
        self._set_enabled("next", False)
    
    def _btn(self, key: str):
        for b in self.buttons:
            if b["key"] == key:
                return b
        return None

    def _set_button_text(self, key, text):
        b = self._btn(key)
        if b:
            b["text"] = text

    def _set_enabled(self, key: str, val: bool):
        b = self._btn(key)
        if b:
            b["enabled"] = bool(val)

    def draw_buttons(self):
        # Footer visible
        pygame.draw.rect(self.pantalla, self.color_fondo, self.footer_rect, border_radius=6)
        pygame.draw.rect(self.pantalla, self.color_fondo,  self.footer_rect, 2, border_radius=6)

        mx, my = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()[0]
 
        for b in self.buttons:
            r = b["rect"]
            enabled = b.get("enabled", True)
            hover = enabled and r.collidepoint((mx, my))
            pressed = hover and click

            if not enabled:
                fill = tuple(max(0, c - 40) for c in self.color_panel)
            elif pressed:
                fill = tuple(max(0, c - 25) for c in self.color_panel)
            elif hover:
                fill = tuple(min(255, c + 15) for c in self.color_panel)
            else:
                fill = self.color_panel

            pygame.draw.rect(self.pantalla, fill, r, border_radius=8)
            pygame.draw.rect(self.pantalla, self.color_grid_line, r, 2, border_radius=8)

            col_text = self.color_titulo if enabled else (160, 150, 140)
            txt = self.font_bases.render(b["text"], True, col_text)
            self.pantalla.blit(txt, txt.get_rect(center=r.center))

    def _on_button(self, key: str):
        if key == "init":
            self._do_init()
        elif key == "play":
            self._do_play_pause()
        elif key == "stop":
            self._do_stop()
        elif key == "prev":
            self._do_prev()
        elif key == "next":
            self._do_next()
        elif key == "quit":
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    def _do_init(self):
        """Inicializa el tablero y deja todo listo para iniciar la simulación."""
        try:
            self.tablero.set_sim_state("init")   # genera mapa, minas, recursos, vehículos
        except Exception as e:
            print("Error al inicializar simulación:", e)
            return

        # habilitar Play después de Init
        self._set_enabled("play", True)
        self._set_button_text("play", "play")

        # deshabilitar lo que no debería tocarse todavía
        self._set_enabled("stop", True)
        self._set_enabled("prev", False)
        self._set_enabled("next", False)

        #print("Tablero inicializado, presioná Play para comenzar la simulación.")

    def _do_play_pause(self):
        """
        Alterna entre Play y Pause.
        - Si la simulación está pausada/inicializada, la inicia o reanuda.
        - Si está corriendo, la pausa.
        También actualiza el texto del botón y el estado visual de los demás.
        """
        sim_state = getattr(self.tablero, "sim_state", None)

        # --- Si está pausada o recién iniciada, arrancar ---
        if sim_state in ("init", "paused", "stopped"):
            # pasamos a running
            self.tablero.set_sim_state("running")

            # si aún no hay rutas (primera vez), generarlas con estrategia J2
            if not getattr(self.tablero, "ruta_activa", {}):
                try:
                    self.tablero.start_simulation()
                except Exception as e:
                    print(f"No se pudo iniciar simulación: {e}")

            # actualizar interfaz: ahora el botón debe decir "Pause"
            self._set_button_text("play", "Pause")
            self._set_enabled("init", False)
            self._set_enabled("stop", True)
            self._set_enabled("prev", False)
            self._set_enabled("next", False)
            #print("Simulación corriendo...")

        # --- Si está corriendo, pausar ---
        elif sim_state == "running":
            self.tablero.toggle_sim_state()  # cambia a "paused"
            self._set_button_text("play", "play")
            self._set_enabled("init", True)
            self._set_enabled("stop", True)
            self._set_enabled("prev", True)
            self._set_enabled("next", True)
            #print("Simulación pausada.")

    def _do_stop(self):
        if hasattr(self.tablero, "set_sim_state"):
            try: self.tablero.set_sim_state("stopped")
            except Exception: pass
        self._set_enabled("pause_resume", False)
        self._set_enabled("stop", False)
        self._set_enabled("prev", False)
        self._set_enabled("next", False)
        self._set_enabled("init", True)

    def _do_prev(self):
        if hasattr(self.tablero, "prev_frame"):
            try: self.tablero.prev_frame()
            except Exception: pass

    def _do_next(self):
        if hasattr(self.tablero, "next_frame"):
            try: self.tablero.next_frame()
            except Exception: pass

    def handle_button_click(self, e):
        """Procesa el clic del mouse y llama a la acción correspondiente."""
        for b in self.buttons:
            if b["enabled"] and b["rect"].collidepoint(e.pos):
                self._on_button(b["key"])
                break

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
        # fondo del header 
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

        timer_line_y = top_y + title_surf.get_height() + 4

        # Puntajes (izq/dcha) — toman self.tablero.puntaje
        p1 = self.tablero.puntaje.get("J1", 0)
        p2 = self.tablero.puntaje.get("J2", 0)
        p1_surf = self.font_bases.render(f"J1: {p1}", True, self.color_titulo)
        p2_surf = self.font_bases.render(f"J2: {p2}", True, self.color_titulo)

        score_offset_y = 0  # probá con 0, 2 o 4 según te guste visualmente

        self.pantalla.blit(p1_surf, (base1_cx - p1_surf.get_width() // 2,
                                    timer_line_y + score_offset_y))
        self.pantalla.blit(p2_surf, (base2_cx - p2_surf.get_width() // 2,
                                    timer_line_y + score_offset_y))
        
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

        # Botones centrados (hover visual)
        mx, my = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()[0]

        for b in self.buttons:
            r = b["rect"]
            hover = r.collidepoint((mx, my))
            pressed = hover and click

            # color según estado
            if pressed:
                fill = tuple(max(0, c - 25) for c in self.color_panel)
            elif hover:
                fill = tuple(min(255, c + 15) for c in self.color_panel)
            else:
                fill = self.color_panel

            pygame.draw.rect(self.pantalla, fill, r, border_radius=8)
            pygame.draw.rect(self.pantalla, self.color_grid_line, r, 2, border_radius=8)

            txt = self.font_bases.render(b["text"], True, self.color_titulo)
            tx = r.centerx - txt.get_width() // 2
            ty = r.centery - txt.get_height() // 2
            self.pantalla.blit(txt, (tx, ty))

    #permite que las bases sean consideradas dentro del tablero
    def cell_to_rect(self, col: int, fila: int, pad: int = 2) -> pygame.Rect:

        #Devuelve el rectángulo 'dibujable' de la celda (col,fila),
        #centrado exactamente dentro del bloque de la celda y con padding simétrico.

        assert 0 <= col < self.columnas and 0 <= fila < self.filas

        # Coordenadas y tamaño "crudo" de la celda (sin pad)
        y = self.gy + fila * self.celda
        h = self.celda

        if col == 0:
            # base izquierda
            x = self.gx
            w = self.base1_rect.width
        elif col == self.columnas - 1:
            # base derecha
            x = self.base2_rect.x
            w = self.base2_rect.width
        else:
            # grilla central (columna 1..N-2)
            x = self.central_rect.x + (col - 1) * self.celda
            w = self.celda

        # Rect "completo" de la celda
        full = pygame.Rect(x, y, w, h)

        # Rect de dibujo: aplicamos pad de forma simétrica y re-centramos
        draw_w = max(1, w - 2 * pad)
        draw_h = max(1, h - 2 * pad)
        rect = pygame.Rect(0, 0, draw_w, draw_h)
        rect.center = full.center  
        return rect

    def draw_item(self, tipo: str, rect: pygame.Rect):

        #Dibuja el sprite ocupando la mayor parte de la celda.
        #Se adapta al tamaño de 'rect' y mantiene proporción.

        img = self.img_cache.get(tipo) if hasattr(self, "img_cache") else self.img.get(tipo)

        # Ratios por categoría (porcentaje del lado de la celda)
        # Ajustalos a gusto (0.90 = 90% del lado útil)
        if tipo in ("J", "M", "C", "A"):              # vehículos
            fill_ratio = 2.5
        elif str(tipo).startswith("PER"):             # personas
            fill_ratio = 1.8
        elif tipo in ("01","02","O1","O2","T1","T2","G1"):  # minas
            fill_ratio = 2
        else:                                         # recursos u otros
            fill_ratio = 1.2


        # Área objetivo dentro de la celda
        max_w = rect.width
        max_h = rect.height

        # Si hay imagen, escalar proporcionalmente a fill_ratio
        if img:
            iw, ih = img.get_size()
            # escala para que entre por ancho y por alto
            s = min((max_w * fill_ratio) / iw, (max_h * fill_ratio) / ih)
            # Tamaño final (con mínimo para que no desaparezcan)
            new_w = max(12, int(iw * s))
            new_h = max(12, int(ih * s))
            # Evitar artefactos (a veces conviene pares)
            if new_w % 2: new_w -= 1
            if new_h % 2: new_h -= 1
            sprite = pygame.transform.smoothscale(img, (new_w, new_h))
            x = rect.centerx - new_w // 2
            y = rect.centery - new_h // 2
            self.pantalla.blit(sprite, (x, y))
            return

        # Fallback si no hay PNG (ej: minas)
        if tipo in ("01","02","O1","O2","T1","T2","G1"):
            colores = {
                "01": (121, 82, 39), "O1": (121, 82, 39),
                "02": (119, 40, 39), "O2": (119, 40, 39),
                "T1": (39, 118, 119),
                "T2": (118, 119, 39),
                "G1": (39, 78, 119),
            }
            color = colores.get(tipo, (200, 0, 0))
            lado = int(min(max_w, max_h) * fill_ratio)
            r = pygame.Rect(rect.centerx - lado//2, rect.centery - lado//2, lado, lado)
            pygame.draw.rect(self.pantalla, color, r, border_radius=3)
            pygame.draw.rect(self.pantalla, (25,25,25), r, 1, border_radius=3)


    def draw_from_tablero(self):
        #Pinta todo lo no-vacío de tablero.matriz usando cell_to_rect(col,fila).
        for fila in range(self.filas):
            for col in range(self.columnas):
                celda = self.tablero.matriz[fila][col]
                if celda not in (0, "0", None, ""):
                    rect = self.cell_to_rect(col, fila, pad=2)

                    if col == 0 or col == self.columnas - 1:
                        extra_scale = 1.1   # 10% más grande en las bases
                    else:
                        extra_scale = 1.0

                    self.draw_item(celda, rect.inflate(
                        int(rect.width * (extra_scale - 1)),
                        int(rect.height * (extra_scale - 1))
                    ))
    #Para cuando tengamos el tema reloj resuelto
    def set_timer(self, seconds:int|None):
        #Actualiza el número que se muestra en el HUD. None = no mostrar.
        self.timer_seconds = seconds

    def _format_time(self, s:int) -> str:
        # 60 -> "01:00", 9 -> "00:09"
        m, ss = divmod(max(0, int(s)), 60)
        return f"{m:02d}:{ss:02d}"

class ButtonBar:
    def __init__(self, rect: pygame.Rect, font: pygame.font.Font,
                 color_panel, color_border, color_text):
        self.rect = rect
        self.font = font
        self.color_panel = color_panel
        self.color_border = color_border
        self.color_text = color_text
        self.buttons = []
        self.callbacks = {}  # key -> function

    def add_button(self, key: str, text: str, enabled=True, callback=None):
        self.callbacks[key] = callback
        self.buttons.append({
            "key": key,
            "text": text,
            "enabled": enabled,
            "rect": None,  # se calcula en layout
        })

    def layout(self, gap=12):
        #Distribuye los botones centrados dentro del rect.
        n = len(self.buttons)
        if n == 0: return
        btn_w, btn_h = 130, 38
        total_w = n * btn_w + (n - 1) * gap
        start_x = self.rect.centerx - total_w // 2
        y = self.rect.centery - btn_h // 2
        for i, b in enumerate(self.buttons):
            x = start_x + i * (btn_w + gap)
            b["rect"] = pygame.Rect(x, y, btn_w, btn_h)

    def draw(self, surface: pygame.Surface):
        mx, my = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()[0]

        for b in self.buttons:
            if not b["rect"]:
                continue
            r = b["rect"]
            enabled = b.get("enabled", True)
            hover = enabled and r.collidepoint((mx, my))
            pressed = hover and click

            if not enabled:
                fill = tuple(max(0, c - 40) for c in self.color_fondo)
            elif pressed:
                fill = tuple(max(0, c - 25) for c in self.color_fondo)
            elif hover:
                fill = tuple(min(255, c + 15) for c in self.color_fondo)
            else:
                fill = self.color_fondo

            pygame.draw.rect(surface, fill, r, border_radius=8)
            pygame.draw.rect(surface, self.color_fondo, r, 2, border_radius=8)

            col_text = self.color_text if enabled else (160, 150, 140)
            txt = self.font.render(b["text"], True, col_text)
            surface.blit(txt, txt.get_rect(center=r.center))

    def handle_event(self, e):
        #Devuelve la key del botón presionado o ejecuta su callback.
        if e.type == pygame.MOUSEBUTTONUP and e.button == 1:
            for b in self.buttons:
                if b["enabled"] and b["rect"] and b["rect"].collidepoint(e.pos):
                    cb = self.callbacks.get(b["key"])
                    if cb:
                        cb()
                    return b["key"]
        return None

    def enable(self, key: str, val: bool):
        for b in self.buttons:
            if b["key"] == key:
                b["enabled"] = bool(val)