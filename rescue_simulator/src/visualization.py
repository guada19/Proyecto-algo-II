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
    def __init__(self, ancho=800, alto=600, tamaño_celdas=20, margen_arriba=40, margen_abajo=40, base_ancho=120):
        pygame.init()
        self.ancho = ancho
        self.alto = alto
        self.tamaño_celdas = tamaño_celdas
        self.margen_arriba = margen_arriba
        self.margen_abajo = margen_abajo
        self.base_ancho = base_ancho
        self.pantalla = pygame.display.set_mode((ancho, alto))
        pygame.display.set_caption("Simulador de Rescate - Mapa")
        self.clock = pygame.time.Clock()

    #Dibuja las cuadriculas del mapa con bases laterales y márgenes
    def draw_grid(self):
        #Cuadricula per se
        arriba = self.margen_arriba
        abajo = self.alto - self.margen_abajo
        izquierda = self.base_ancho
        derecha = self.ancho - self.base_ancho
        
        # Fondo de mapa central
        pygame.draw.rect(self.pantalla, COLOR_MAPA, (izquierda, arriba, derecha - izquierda, abajo - arriba))

        # Cuadrícula dentro del área central
        cols = (derecha - izquierda) // self.tamaño_celdas
        rows = (abajo - arriba) // self.tamaño_celdas

        for c in range(cols + 1):
            x = izquierda + c * self.tamaño_celdas
            pygame.draw.line(self.pantalla, COLOR_LINEA, (x, arriba), (x, abajo), 2)
        for r in range(rows + 1):
            y = arriba + r * self.tamaño_celdas
            pygame.draw.line(self.pantalla, COLOR_LINEA, (izquierda, y), (derecha, y), 2)

        # Bases laterales
        pygame.draw.rect(self.pantalla, COLOR_BASE1, (0, arriba, self.base_ancho, abajo - arriba))
        pygame.draw.rect(self.pantalla, COLOR_BASE2, (derecha, arriba, self.base_ancho, abajo - arriba))

        # Etiquetas opcionales (cuando tengamos más cosas se mejora)
    """ font = pygame.font.SysFont(None, 28)
        text1 = font.render("BASE JUGADOR 1", True, (255, 255, 255))
        text2 = font.render("BASE JUGADOR 2", True, (255, 255, 255))

        # centradas verticalmente
        self.pantalla.blit(text1, (10, self.alto // 2 - 10))
        self.pantalla.blit(text2, (self.ancho - self.base_ancho + 10, self.alto // 2 - 10))
        """

    #Funcion que mantiene la ventana abierta
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.pantalla.fill(COLOR_FONDO)
            self.draw_grid()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()