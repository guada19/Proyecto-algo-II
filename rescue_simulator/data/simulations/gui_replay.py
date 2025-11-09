import pygame
pygame.init()    
import sys
import os


# ruta relativa al archivo actual
font_1 = os.path.join(os.path.dirname(__file__), "..", "fonts", "RubikDirt-Regular.ttf")
font_2 = os.path.join(os.path.dirname(__file__), "..", "fonts", "Galindo-Regular.ttf")
font_3 = os.path.join(os.path.dirname(__file__), "..", "fonts", "trebuc.ttf")


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

    # --- Zona del tablero central (entre bases) ---
    board_rect = getattr(viz, "central_rect", pygame.Rect(0, 0, viz.ancho, viz.alto))

    # --- Cálculo del panel centrado ---
    panel_w = int(board_rect.width * 0.6)
    panel_h = 280
    panel_rect = pygame.Rect(0, 0, panel_w, panel_h)
    panel_rect.center = board_rect.center

    # --- Botones centrados dentro del panel ---
    boton_w, boton_h = int(panel_w * 0.50), 50
    gap = 20
    boton_replay = pygame.Rect(0, 0, boton_w, boton_h)
    boton_salir = pygame.Rect(0, 0, boton_w, boton_h)
    boton_replay.centerx = boton_salir.centerx = panel_rect.centerx
    boton_replay.centery = panel_rect.centery + 15
    boton_salir.top = boton_replay.bottom + gap
    boton_salir.centerx = panel_rect.centerx
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if boton_replay.collidepoint(event.pos):
                    if hasattr(viz, "enter_replay_view"):
                        viz.enter_replay_view()
                    try:
                        viz._set_enabled("prev", True)
                        viz._set_enabled("next", True)
                    except Exception:
                        pass    
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
        overlay = pygame.Surface((board_rect.width, board_rect.height), pygame.SRCALPHA)
        overlay.fill((78, 77, 52, 70))  # negro con transparencia
        viz.pantalla.blit(overlay, board_rect.topleft)

        # Panel central
        pygame.draw.rect(viz.pantalla, (55, 55, 49), panel_rect, border_radius=18)

        # Título
        titulo = fuente_titulo.render("Simulación terminada", True, (203, 196, 177))
        subtitulo = fuente_subtitulo.render(cartel, True, (203, 196, 177))
        viz.pantalla.blit(titulo, titulo.get_rect(center=(panel_rect.centerx, panel_rect.top + 60)))
        viz.pantalla.blit(subtitulo, subtitulo.get_rect(center=(panel_rect.centerx, panel_rect.top + 105)))


        # Botones
        mouse_pos = pygame.mouse.get_pos()
        color_replay = (10, 32, 11) if boton_replay.collidepoint(mouse_pos) else (17, 53, 19)
        color_salir = (67, 23, 21) if boton_salir.collidepoint(mouse_pos) else (112, 38, 35)

        pygame.draw.rect(viz.pantalla, color_replay, boton_replay, border_radius=12)
        pygame.draw.rect(viz.pantalla, color_salir, boton_salir, border_radius=12)

        texto_replay = fuente_boton.render("Reproducir replay", True, (108, 121, 109))
        texto_salir = fuente_boton.render("Salir", True, (169, 125, 123))

        viz.pantalla.blit(texto_replay, texto_replay.get_rect(center=boton_replay.center))
        viz.pantalla.blit(texto_salir, texto_salir.get_rect(center=boton_salir.center))

        pygame.display.flip()
        reloj.tick(30)


def modo_replay_misma_pantalla(viz, replay, auto_play=True, desde_frame=0):
    """
    Reproduce automáticamente el replay, pero permite usar flechas para moverse frame a frame.
    """
    frames = replay.cargar_pickle("partida_actual.pkl")

    if not frames:
        print("No hay frames guardados en el replay.")
        return

    index = desde_frame
    total = len(frames)
    reloj = pygame.time.Clock()

    reproduciendo = auto_play  # True = corre solo; False = control manual
    velocidad_fps = 4    # velocidad del replay automático

    fuente_info = pygame.font.Font(font_3, 24)

    # Entrar (o reafirmar) modo repetición y poner los botones en su estado inicial
    try:
        if hasattr(viz, "enter_replay_view"):
            viz.enter_replay_view()
        # asegurar que la simulación está detenida para no auto-bloquear controles
        if hasattr(viz, "tablero") and hasattr(viz.tablero, "set_sim_state"):
            viz.tablero.set_sim_state("stopped")

    except Exception as _e:
        pass    

    if hasattr(viz, "enter_replay_view"):
        viz.enter_replay_view()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                ruta_pos = os.path.join(replay.save_dir, "posicion_replay.txt")
                with open(ruta_pos, "w") as f:
                    f.write(str(index))
                if hasattr(viz, "exit_replay_view"):
                    viz.exit_replay_view()
                pygame.quit()
                return
            
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                viz.handle_button_click(event)
                btn = getattr(viz, "last_button_pressed", None)
                if btn == "prev":
                    index = max(index - 1, 0)
                    reproduciendo = False
                elif btn == "next":
                    index = min(index + 1, total - 1)
                    reproduciendo = False
                elif btn == "init":
                    print("[INFO] Se presionó INIT dentro del modo replay. Reiniciando todo...")
                    replay.reset()
                    if hasattr(viz, "exit_replay_view"):
                        viz.exit_replay_view()                    
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
                    ruta_pos = os.path.join(replay.save_dir, "posicion_replay.txt")
                    with open(ruta_pos, "w") as f:
                        f.write(str(index))
                    if hasattr(viz, "exit_replay_view"):
                        viz.exit_replay_view()                        
                    return

        # Actualizar frame
        if reproduciendo:
            index += 1
            if index >= total:
                if hasattr(viz, "exit_replay_view"):
                    viz.exit_replay_view()
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
