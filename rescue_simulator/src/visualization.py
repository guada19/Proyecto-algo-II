import pygame
import os

# ruta relativa al archivo actual
font_1 = os.path.join(os.path.dirname(__file__), "..", "data", "fonts", "RubikDirt-Regular.ttf")
font_2 = os.path.join(os.path.dirname(__file__), "..", "data", "fonts", "Galindo-Regular.ttf")
font_3 = os.path.join(os.path.dirname(__file__), "..", "data", "fonts", "Sixtyfour-Regular.ttf")

# Clase simple para botones
class Button:
    def __init__(self, x, y, w, h, text, color, hover_color, action=None, font_size=16):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        self.action = action
        self.font = pygame.font.Font(font_2, font_size)
        self.disabled = False
        self._saved_colors = (color, hover_color)
        
    def draw(self, surface):
        if self.disabled:
            # apariencia deshabilitada (gris tenue), sin efecto hover
            self.current_color = (120, 120, 120)
        else:
            mouse_pos = pygame.mouse.get_pos()
            if self.rect.collidepoint(mouse_pos):
                self.current_color = self.hover_color
            else:
                self.current_color = self.color
            
        pygame.draw.rect(surface, self.current_color, self.rect, 0, border_radius=4)
        pygame.draw.rect(surface, (25, 25, 25), self.rect, 2, border_radius=4)
        
        # Ajuste para que el texto encaje
        text_surf = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def handle_event(self, event):
        # Ignorar eventos si está deshabilitado
        if self.disabled:
            return False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                if self.action:
                    self.action()
                return True
        return False

    def disable(self):
        self.disabled = True

    def enable(self):
        self.disabled = False

#Clase que muestra todo en pantalla
class Visualizer:
    
    def __init__(self, tablero, ancho=1200, alto=700):
        
        # Colores base
        self.color_fondo = (78, 77, 52)     
        self.color_grid_line = (60, 54, 49)  
        self.color_panel = (143, 125, 110)    
        self.color_grid_bg = (149, 135, 122) 
        self.color_borde = (57, 50, 44)      
        self.color_titulo = (210, 180, 140)  
        self.color_button_default = (100, 149, 237) 
        self.color_button_hover = (65, 105, 225) 
        self.color_quit = (200, 50, 50) # Rojo para salir

        # --- títulos y header ---
        self.title = "Rescue Simulator"    
        self.header_h = 40                 

        self.tablero = tablero
        self.ancho = ancho
        self.alto = alto

        pygame.init()
        pygame.font.init()
        # Inicializar mixer para reproducir sonidos (fallar silenciosamente si no disponible)
        self.collision_sound = None
        try:
            pygame.mixer.init()
            sound_path = os.path.join(os.path.dirname(__file__), "..", "data", "sounds", "collision.wav")
            if os.path.exists(sound_path):
                self.collision_sound = pygame.mixer.Sound(sound_path)
        except Exception:
            # no detener ejecución si mixer falla o archivo no existe
            self.collision_sound = None
        self.pantalla = pygame.display.set_mode((self.ancho, self.alto))
        self.font_titulo = pygame.font.Font(font_1, 35)
        self.font_bases = pygame.font.Font(font_2, 18)
        self.font_button = pygame.font.Font(font_2, 16)
        self.font_label = pygame.font.Font(font_2, 12) # Fuente para la etiqueta del vehículo
        pygame.display.set_caption("Simulador - Tablero")
        self.clock = pygame.time.Clock()

        # Reducimos ligeramente el ancho de los paneles laterales (base_px)
        # para dejar más espacio a la grilla central en 50x50.
        self._compute_layout(margen = 40, base_px = 70)

        self._cargar_sprites()

        self.buttons = self._create_buttons()
        # Track last frame index to play collision sound only once per new live frame
        self._last_played_collision_frame = -1

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

    def _create_buttons(self):
        """Crea los botones de control y administra su habilitación según estado."""
        button_w = 110
        button_h = 30
        spacing = 8

        total_buttons_w = 6 * button_w + 5 * spacing
        start_x = (self.ancho - total_buttons_w) // 2
        # colocar botones debajo del mapa (debajo de la grilla central)
        start_y = self.gy + self.central_h + 10

        buttons = []
        x = start_x

        # INIT (habilitado inicialmente)
        init_btn = Button(x, start_y, button_w, button_h, "INIT",
                          self.color_button_default, self.color_button_hover, action=None)
        def _init_action():
            # iniciar simulación
            self.tablero.set_sim_state("init")
            # UI: INIT deshabilitado, PAUSE y STOP habilitados, PREV/NEXT deshabilitados
            init_btn.disable()
            pause_btn.enable()
            stop_btn.enable()
            prev_btn.disable()
            next_btn.disable()
        init_btn.action = _init_action
        buttons.append(init_btn)
        x += button_w + spacing

        # PAUSE/RESUME (deshabilitado hasta INIT)
        pause_btn = Button(x, start_y, button_w, button_h, "PAUSE/RESUME",
                           self.color_button_default, self.color_button_hover, action=None, font_size=12)
        def _pause_action():
            # alternar estado en el modelo
            self.tablero.toggle_sim_state()
            # Si ahora está en pausa, habilitar prev/next; si está corriendo, deshabilitarlos.
            if self.tablero.sim_state == "paused":
                prev_btn.enable()
                next_btn.enable()
            else:
                prev_btn.disable()
                next_btn.disable()
        pause_btn.action = _pause_action
        buttons.append(pause_btn)
        x += button_w + spacing

        # STOP (deshabilitado hasta INIT)
        stop_btn = Button(x, start_y, button_w, button_h, "STOP",
                          self.color_button_default, self.color_button_hover, action=None)
        def _stop_action():
            self.tablero.set_sim_state("stopped")
            # UI: INIT habilitado, PAUSE/STOP deshabilitados, PREV/NEXT deshabilitados
            init_btn.enable()
            pause_btn.disable()
            stop_btn.disable()
            prev_btn.disable()
            next_btn.disable()
        stop_btn.action = _stop_action
        buttons.append(stop_btn)
        x += button_w + spacing

        # PREV (<<) - deshabilitado hasta pausa
        prev_btn = Button(x, start_y, button_w, button_h, "<< (Prev)",
                          self.color_button_default, self.color_button_hover,
                          lambda: self.tablero.prev_frame())
        buttons.append(prev_btn)
        x += button_w + spacing

        # NEXT (>>) - deshabilitado hasta pausa
        next_btn = Button(x, start_y, button_w, button_h, ">> (Next)",
                          self.color_button_default, self.color_button_hover,
                          lambda: self.tablero.next_frame())
        buttons.append(next_btn)
        x += button_w + spacing

        # QUIT (siempre habilitado)
        buttons.append(Button(x, start_y, button_w, button_h, "QUIT",
                              self.color_quit, (255, 0, 0),
                              lambda: pygame.event.post(pygame.event.Event(pygame.QUIT))))

        # Ajustar layout vertical (no desplazar gy; los botones están fuera del área de la grilla)
        self.buttons_h = button_h + spacing

        # ESTADOS INICIALES: antes de presionar INIT o después de STOP
        # pause, stop, prev, next deben estar deshabilitados
        pause_btn.disable()
        stop_btn.disable()
        prev_btn.disable()
        next_btn.disable()

        return buttons


    #Bucle que mantiene el juego corriendo
    def run(self):
        corriendo = True
        while corriendo:
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    corriendo = False
                for btn in self.buttons:
                    btn.handle_event(e)

            self.pantalla.fill((self.color_fondo))  
            self.draw_grid()
            self.draw_buttons()
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
        self.buttons_h = 0 

        # área total util (dentro del margen)
        avail_w = self.ancho - 2*self.margen
        avail_h = self.alto  - 2*self.margen - self.header_h

        # columnas centrales: ahora usamos todas las columnas como celdas iguales
        # (las bases se dibujan como paneles laterales fuera de la grilla)
        central_cols = max(self.columnas, 1)

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

    def draw_buttons(self):
        """Dibuja todos los botones en la pantalla."""
        for btn in self.buttons:
            btn.draw(self.pantalla)


    def draw_grid(self):
        gx = self.gx
        gy = self.gy
        h = self.central_h

        # rects
        base_j1    = (self.gx, self.gy, self.base_w, h) 
        central_x    = self.gx + self.base_w
        central_rect = (central_x, self.gy, self.central_w, h)
        base_j2  = (central_x + self.central_w, self.gy, self.base_w, h) 

        # ---------- HEADER y Títulos ----------
        header_rect = (self.margen, self.margen, self.ancho - 2*self.margen, self.header_h)
        pygame.draw.rect(self.pantalla, self.color_fondo, header_rect, 0, border_radius=4)
        pygame.draw.rect(self.pantalla, self.color_fondo, header_rect, 2, border_radius=4)
        # Mostrar contador de pasos en la esquina superior derecha del header (tomado del frame actual)
        try:
            frame = self.tablero.obtener_frame_actual()
            pasos = frame.get("step_count", getattr(self.tablero, "step_count", 0))
        except Exception:
            pasos = getattr(self.tablero, "step_count", 0)
        contador_s = f"Pasos: {int(pasos)}"
        cnt_surf = self.font_bases.render(contador_s, True, (240, 240, 240))
        cnt_x = header_rect[0] + header_rect[2] - 12 - cnt_surf.get_width()
        cnt_y = header_rect[1] + (header_rect[3] - cnt_surf.get_height()) // 2
        self.pantalla.blit(cnt_surf, (cnt_x, cnt_y))

        title_surf = self.font_titulo.render(self.title, True, self.color_titulo)
        title_x = header_rect[0] + (header_rect[2] - title_surf.get_width()) // 2
        title_y = header_rect[1] + (header_rect[3] - title_surf.get_height()) // 2
        self.pantalla.blit(title_surf, (title_x, title_y))

        base1_surf = self.font_bases.render("Base J1", True, self.color_titulo)
        base2_surf = self.font_bases.render("Base J2", True, self.color_titulo)

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
        cols_centro = max(self.columnas, 1)

        inset = 1 
        inner_left   = central_x + inset
        inner_top    = self.gy + inset
        inner_right  = central_x + self.central_w - inset
        inner_bottom = self.gy + h - inset
        
        # Verticales
        for c in range(1, cols_centro):
            x = inner_left + c * (self.celda)
            pygame.draw.line(self.pantalla, self.color_grid_line, (x, inner_top), (x, inner_bottom), 2)

        # Horizontales
        for r in range(1, self.filas):
            y = inner_top + r * (self.celda)
            pygame.draw.line(self.pantalla, self.color_grid_line, (inner_left, y), (inner_right, y), 2)

        # borde del tablero
        pygame.draw.rect(self.pantalla, self.color_borde, central_rect, 3)


    def cell_to_rect(self, col, fila, pad=2):
        """Devuelve el rect para una celda lógica (col,fila)."""
        assert 0 <= col < self.columnas and 0 <= fila < self.filas

        y = self.gy + fila * self.celda
        h = self.celda

        # Todas las columnas son celdas iguales; la grilla está desplazada por base_w
        x = self.gx + self.base_w + col * self.celda
        w = self.celda

        return pygame.Rect(x + pad, y + pad, max(1, w - 2*pad), max(1, h - 2*pad))

    

    
    def draw_item(self, label, rect):
        """
        Dibuja un item en 'rect'. Si es un vehículo, dibuja el círculo 
        y la etiqueta de identificación (Punto 3).
        """
        base_h = rect.height
        radio  = max(5, int(base_h * 1.5))
        lado   = max(6, int(base_h * 2.0))

        # Tipos de Minas
        if label in ("01", "02", "T1", "T2", "G1"):
            colores_mina = {
                "01": (121, 82, 39), "02": (119, 40, 39),    
                "T1": (39, 118, 119), "T2": (118, 119, 39),     
                "G1": (39, 78, 119),      
            }
            color = colores_mina.get(label, (200, 0, 0))
            r = pygame.Rect(rect.centerx - lado // 2,
                            rect.centery - lado // 2, lado, lado)
            pygame.draw.rect(self.pantalla, color, r)
            pygame.draw.rect(self.pantalla, (25, 25, 25), r, 1)
            return

        # Tipos de Recursos/Mercancías
        if label in ("PER", "R", "r", "m", "a"):
            color = {
                "PER": (204, 153, 179), # Persona
                "R": (164, 179, 53),    # Alimento (Recurso)
                "m": (204, 178, 153),   # Medicamento
                "a": (179, 204, 153),   # Armamento
                "r": (153, 179, 204),   # Ropa
            }.get(label, (160, 160, 160))
            
            pygame.draw.circle(self.pantalla, color, rect.center, radio)
            pygame.draw.circle(self.pantalla, (25, 25, 25), rect.center, radio, 1)  
            return

        # Tipos de Vehículos (Ej: J1, M2, C1, A2) - Dibujo y Etiqueta
        if len(label) == 2 and label[1].isdigit():
            tipo_vehiculo = label[0]
            jugador = int(label[1])
            
            color = {
                "J": (164, 179,  53),    # Jeep
                "M": (246, 154,  84),    # Moto
                "C": (243,  92,  72),    # Camión
                "A": (255, 240, 130),    # Auto
            }.get(tipo_vehiculo, (100, 100, 100))

            # Dibujar Círculo del Vehículo
            pygame.draw.circle(self.pantalla, color, rect.center, radio)
            pygame.draw.circle(self.pantalla, (25, 25, 25), rect.center, radio, 1) 
            
            # Dibujar Etiqueta (Punto 3)
            text_surf = self.font_label.render(label, True, (0, 0, 0))
            text_rect = text_surf.get_rect(center=rect.center)
            self.pantalla.blit(text_surf, text_rect)
            return


    def draw_from_tablero(self):
        """Dibuja primero los radios de minas (según el frame guardado) y luego los items."""
        # rect de la zona cuadriculada central (para recortar dibujo)
        central_x = self.gx + self.base_w
        central_rect = pygame.Rect(central_x, self.gy, self.central_w, self.central_h)
        old_clip = self.pantalla.get_clip()
        self.pantalla.set_clip(central_rect)

        # Obtener frame guardado para el índice actual
        frame = self.tablero.obtener_frame_actual()
        minas_overlay = frame.get("minas_overlay", [])

        # Dibujar overlays de minas según el frame (se dibujan solo dentro de la cuadricula)
        for mo in minas_overlay:
            if mo.get("estado") != "activa":
                continue
            if not mo.get("visible", True):
                continue
            fila, col = mo.get("pos", (None, None))
            if fila is None:
                continue
            if not (0 <= fila < self.filas and 0 <= col < self.columnas):
                continue
            cell_rect = self.cell_to_rect(col=col, fila=fila, pad=0)
            tipo = mo.get("tipo")
            radio_cells = int(mo.get("radio", 0))

            if tipo in ("01", "02", "G1"):
                radius_px = max(1, radio_cells * self.celda)
                surf_size = radius_px * 2 + 4
                s = pygame.Surface((surf_size, surf_size), pygame.SRCALPHA)
                pygame.draw.circle(s, (255, 200, 0, 70), (surf_size//2, surf_size//2), radius_px)
                pygame.draw.circle(s, (200, 120, 0, 220), (surf_size//2, surf_size//2), radius_px, 2)
                blit_pos = (cell_rect.centerx - surf_size//2, cell_rect.centery - surf_size//2)
                self.pantalla.blit(s, blit_pos)
            elif tipo == "T1":
                span = radio_cells or 10
                left_col = max(1, col - span)
                right_col = min(self.columnas - 2, col + span)
                left_r = self.cell_to_rect(col=left_col, fila=fila, pad=0)
                right_r = self.cell_to_rect(col=right_col, fila=fila, pad=0)
                x = left_r.x
                y = left_r.y
                w = (right_r.x + right_r.width) - x
                h = left_r.height
                s = pygame.Surface((w, h), pygame.SRCALPHA)
                s.fill((200, 60, 60, 60))
                self.pantalla.blit(s, (x, y))
                pygame.draw.rect(self.pantalla, (200, 20, 20), (x, y, w, h), 2, border_radius=3)
            elif tipo == "T2":
                span = radio_cells or 5
                top_row = max(0, fila - span)
                bottom_row = min(self.filas - 1, fila + span)
                top_r = self.cell_to_rect(col=col, fila=top_row, pad=0)
                bottom_r = self.cell_to_rect(col=col, fila=bottom_row, pad=0)
                x = top_r.x
                y = top_r.y
                w = top_r.width
                h = (bottom_r.y + bottom_r.height) - y
                s = pygame.Surface((w, h), pygame.SRCALPHA)
                s.fill((160, 160, 220, 60))
                self.pantalla.blit(s, (x, y))
                pygame.draw.rect(self.pantalla, (40, 40, 160), (x, y, w, h), 2, border_radius=3)

        # restaurar clip antes de dibujar items
        self.pantalla.set_clip(old_clip)

    

        # usar la matriz del frame actual
        frame = self.tablero.obtener_frame_actual()
        matriz_actual = frame.get("matriz", self.tablero.matriz)
       
        for fila in range(self.filas):
            for col in range(self.columnas):
                celda = matriz_actual[fila][col] 
                if celda in ("0", 0, None, ""):
                    continue
                rect = self.cell_to_rect(col, fila, pad=4)
                self.draw_item(celda, rect)

        # Dibujar recuadros rojos para las colisiones del frame
        col_vis = set(frame.get("colisiones", set()))
        col_just = set(frame.get("colisiones_just_added", set()))
        if col_vis:
            outline_color = (200, 20, 20)
            for pos in list(col_vis):
                fila, col = pos
                if not (0 <= fila < self.filas and 0 <= col < self.columnas):
                    continue
                rect = self.cell_to_rect(col=col, fila=fila, pad=1)
                pygame.draw.rect(self.pantalla, outline_color, rect, 3, border_radius=3)

        # Reproducir sonido de colisión solo si estamos mostrando el frame más reciente (live)
        # y solo una vez por cambio de frame para no repetir a 60 FPS.
        current_index = self.tablero.indice_historial
        if current_index == len(self.tablero.historial_matrices) - 1:
            if col_just and current_index != self._last_played_collision_frame:
                try:
                    if self.collision_sound:
                        self.collision_sound.play()
                except Exception:
                    pass
                self._last_played_collision_frame = current_index



        # Si la simulación está detenida por STOP, mostrar overlay "juego finalizado"
        if getattr(self.tablero, "game_finished", False) and self.tablero.sim_state == "stopped":
            # cuadro semi-transparente centrado con mensaje
            overlay_w, overlay_h = 420, 120
            center_x = (self.ancho - overlay_w) // 2
            center_y = (self.alto - overlay_h) // 2
            s = pygame.Surface((overlay_w, overlay_h), pygame.SRCALPHA)
            s.fill((0, 0, 0, 180))  # fondo negro semi-transparente
            # rect borde
            pygame.draw.rect(s, (255, 255, 255, 220), (0, 0, overlay_w, overlay_h), 2, border_radius=6)
            # texto
            msg = "juego finalizado"
            text_surf = self.font_titulo.render(msg, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=(overlay_w // 2, overlay_h // 2))
            s.blit(text_surf, text_rect)
            self.pantalla.blit(s, (center_x, center_y))
