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
    #Inicializa pygames
    #settea tamaño de la ventana
    def __init__(self, width=800, height=600, cell_size=20, margin_top=40, margin_bottom=40, base_width=120):
        pygame.init()
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.margin_top = margin_top
        self.margin_bottom = margin_bottom
        self.base_width = base_width
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Simulador de Rescate - Mapa")
        self.clock = pygame.time.Clock()

    #Dibuja las cuadriculas del mapa con bases laterales y márgenes
    def draw_grid(self):
        #Cuadricula per se
        top = self.margin_top
        bottom = self.height - self.margin_bottom
        left = self.base_width
        right = self.width - self.base_width
        
        # Fondo de mapa central
        pygame.draw.rect(self.screen, COLOR_MAPA, (left, top, right - left, bottom - top))

        # Cuadrícula dentro del área central
        cols = (right - left) // self.cell_size
        rows = (bottom - top) // self.cell_size

        for c in range(cols + 1):
            x = left + c * self.cell_size
            pygame.draw.line(self.screen, COLOR_LINEA, (x, top), (x, bottom), 2)
        for r in range(rows + 1):
            y = top + r * self.cell_size
            pygame.draw.line(self.screen, COLOR_LINEA, (left, y), (right, y), 2)

        # Bases laterales
        pygame.draw.rect(self.screen, COLOR_BASE1, (0, top, self.base_width, bottom - top))
        pygame.draw.rect(self.screen, COLOR_BASE2, (right, top, self.base_width, bottom - top))

        # Etiquetas opcionales (cuando tengamos más cosas se mejora)
    """ font = pygame.font.SysFont(None, 28)
        text1 = font.render("BASE JUGADOR 1", True, (255, 255, 255))
        text2 = font.render("BASE JUGADOR 2", True, (255, 255, 255))

        # centradas verticalmente
        self.screen.blit(text1, (10, self.height // 2 - 10))
        self.screen.blit(text2, (self.width - self.base_width + 10, self.height // 2 - 10))
        """

    #Funcion que mantiene la ventana abierta
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.screen.fill(COLOR_FONDO)
            self.draw_grid()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()