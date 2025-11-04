import pygame
pygame.init()    
import sys
import os


# ruta relativa al archivo actual
font_1 = os.path.join(os.path.dirname(__file__), "..", "fonts", "RubikDirt-Regular.ttf")
font_2 = os.path.join(os.path.dirname(__file__), "..", "fonts", "Galindo-Regular.ttf")
font_3 = os.path.join(os.path.dirname(__file__), "..", "fonts", "Sixtyfour-Regular.ttf")


def mostrar_menu_final(viz, replay):
    """
    Pantalla de fin de simulación con estilo 'cartel emergente'.
    """
    
    ganador = viz.definir_ganador()
    cartel = "El ganador es:  " + ganador if ganador else "Es un empate"
    
    fuente_titulo = pygame.font.Font(font_1, 35)
    fuente_boton = pygame.font.Font(font_2, 18)
    fuente_subtitulo = pygame.font.Font(font_1, 20)
    reloj = pygame.time.Clock()

    # Definir botones
    boton_replay = pygame.Rect(250, 250, 250, 70)
    boton_salir = pygame.Rect(250, 340, 250, 70)
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if boton_replay.collidepoint(event.pos):
                    modo_replay_misma_pantalla(viz, replay)
                    return
                elif boton_salir.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

        # Fondo del tablero
        viz.pantalla.fill(viz.color_fondo)
        viz.draw_grid()
        viz.draw_buttons()
        viz.draw_mine_radius()
        viz.draw_from_tablero()

        # Capa semi-transparente
        overlay = pygame.Surface(viz.pantalla.get_size(), pygame.SRCALPHA)
        overlay.fill((78, 77, 52, 70))  # negro con transparencia
        viz.pantalla.blit(overlay, (0, 0))

        # Panel central
        pygame.draw.rect(viz.pantalla, (40, 40, 40), (150, 150, 450, 300), border_radius=20)
        pygame.draw.rect(viz.pantalla, (200, 200, 200), (150, 150, 450, 300), 3, border_radius=20)

        # Título
        titulo = fuente_titulo.render("Simulación terminada", True, (255, 255, 255))
        viz.pantalla.blit(titulo, (180, 170))

        altura_titulo = titulo.get_height()

        sub_titulo = fuente_subtitulo.render(cartel, True, (255, 255, 255))
        viz.pantalla.blit(sub_titulo, (250, 180 + altura_titulo))
        
        # Botones
        mouse_pos = pygame.mouse.get_pos()
        color_replay = (143, 125, 110) if boton_replay.collidepoint(mouse_pos) else (60, 180, 60)
        color_salir = (143, 125, 110) if boton_salir.collidepoint(mouse_pos) else (180, 60, 60)

        pygame.draw.rect(viz.pantalla, color_replay, boton_replay, border_radius=15)
        pygame.draw.rect(viz.pantalla, color_salir, boton_salir, border_radius=15)

        texto_replay = fuente_boton.render("Reproducir replay", True, (0, 0, 0))
        texto_salir = fuente_boton.render("Salir", True, (0, 0, 0))

        viz.pantalla.blit(texto_replay, (boton_replay.x + 25, boton_replay.y + 15))
        viz.pantalla.blit(texto_salir, (boton_salir.x + 95, boton_salir.y + 15))

        pygame.display.flip()
        reloj.tick(30)


def modo_replay_misma_pantalla(viz, replay):
    """
    Reproduce automáticamente el replay, pero permite usar flechas para moverse frame a frame.
    """
    frames = replay.cargar_pickle("partida_actual.pkl")

    if not frames:
        print("No hay frames guardados en el replay.")
        return

    index = 0
    total = len(frames)
    reloj = pygame.time.Clock()

    reproduciendo = True  # True = corre solo; False = control manual
    velocidad_fps = 4    # velocidad del replay automático

    fuente_info = pygame.font.Font(None, 32)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    index = min(index + 1, total - 1)
                    reproduciendo = False
                elif event.key == pygame.K_LEFT:
                    index = max(index - 1, 0)
                    reproduciendo = False
                elif event.key == pygame.K_SPACE:
                    reproduciendo = not reproduciendo  # pausar/reanudar
                elif event.key == pygame.K_ESCAPE:
                    return

        # Actualizar frame
        if reproduciendo:
            index += 1
            if index >= total:
                mostrar_menu_final(viz, replay)
                return

        frame = frames[index]
        
        # 1. Almacenar el tablero actual del Visualizer
        tablero_original = viz.tablero 
        # 2. Reemplazarlo temporalmente con el tablero del frame de replay
        viz.tablero = frame["tablero"] 
        # 3. Llamar a la nueva función centralizada de dibujo
        dibujar_frame_replay(viz, frame)        
        # 4. Restaurar el tablero original (el de la simulación principal)
        viz.tablero = tablero_original 
        # --------------------------
        
        # Mostrar info arriba a la izquierda
        texto_info = fuente_info.render(
            f"Frame {index + 1}/{total}  |  {'Reproduciendo' if reproduciendo else 'Pausado'}",
            True, (255, 255, 255)
        )
        viz.pantalla.blit(texto_info, (15, 10))

        pygame.display.flip()
        reloj.tick(velocidad_fps)


def dibujar_frame_replay(viz, frame_data):
    """
    Usa el nuevo método del visualizador para dibujar el frame del replay.
    """
    viz.draw_replay_frame(frame_data)
