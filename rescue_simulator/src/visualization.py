import pygame
pygame.init()
import os
import math

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
    
    def __init__(self, tablero, ancho=1400, alto=900):
        
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

        self.buttons = self._create_buttons()

    def _create_buttons(self):
        """Crea los botones de control para la simulación. (Punto 4 y 5)"""
        button_w = 110  # Aumentado para texto más largo
        button_h = 30
        spacing = 8
        
        # 6 botones: INIT, PAUSE/RESUME, STOP, <<, >>, QUIT
        total_buttons_w = 6 * button_w + 5 * spacing
        start_x = (self.ancho - total_buttons_w) // 2 
        start_y = self.margen + self.header_h + 10 

        buttons = []
        x = start_x

        # Creamos INIT sin acción primero para poder referenciar al botón y deshabilitarlo
        init_btn = Button(x, start_y, button_w, button_h, "INIT", 
                          self.color_button_default, self.color_button_hover, 
                          action=None)
        # acción: iniciar simulación y deshabilitar INIT hasta que se presione STOP
        def _init_action():
            self.tablero.set_sim_state("init")
            init_btn.disable()
        init_btn.action = _init_action
        buttons.append(init_btn)

        x += button_w + spacing
        
        buttons.append(Button(x, start_y, button_w, button_h, "PAUSE/RESUME", 
                              self.color_button_default, self.color_button_hover, 
                              lambda: self.tablero.toggle_sim_state(), font_size=12)) # Letra más pequeña para que encaje
        x += button_w + spacing

        # STOP debe re-habilitar INIT
        stop_btn = Button(x, start_y, button_w, button_h, "STOP", 
                          self.color_button_default, self.color_button_hover, action=None)
        def _stop_action():
            self.tablero.set_sim_state("stopped")
            # re-habilitar INIT cuando se detenga el juego
            init_btn.enable()
        stop_btn.action = _stop_action
        buttons.append(stop_btn)
        x += button_w + spacing
        
        buttons.append(Button(x, start_y, button_w, button_h, "<< (Prev)", 
                              self.color_button_default, self.color_button_hover, 
                              lambda: self.tablero.prev_frame()))
        x += button_w + spacing
        
        buttons.append(Button(x, start_y, button_w, button_h, ">> (Next)", 
                              self.color_button_default, self.color_button_hover, 
                              lambda: self.tablero.next_frame()))
        x += button_w + spacing

        buttons.append(Button(x, start_y, button_w, button_h, "QUIT", 
                              self.color_quit, (255, 0, 0), 
                              lambda: pygame.event.post(pygame.event.Event(pygame.QUIT)))) # Botón de salida (Punto 5)

        # Se ajusta la posición vertical de la grilla principal
        self.buttons_h = button_h + spacing 
        self.gy += self.buttons_h 

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
        cols_centro = max(self.columnas - 2, 1)

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

    
    def draw_item(self, label, rect):
        """
        Dibuja un item en 'rect'. Si es un vehículo, dibuja el círculo 
        y la etiqueta de identificación (Punto 3).
        """
        base_h = rect.height
        radio  = max(5, int(base_h * 0.45))
        lado   = max(6, int(base_h * 0.90))

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
    

        matriz_actual = self.tablero.obtener_matriz_historial()
        
        for fila in range(self.filas):
            for col in range(self.columnas):
                celda = matriz_actual[fila][col] 
                if celda in ("0", 0, None, ""):
                    continue
                rect = self.cell_to_rect(col, fila, pad=4)
                self.draw_item(celda, rect)




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
