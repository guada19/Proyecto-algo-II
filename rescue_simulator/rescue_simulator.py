import pygame
from src.map_manager import Tablero
from src.visualization import Visualizer
from data.simulations.replay_manager import ReplayManager
from data.simulations.gui_replay import *
import copy

def main():
    """
    #Main rama Andre
    tablero = Tablero(ancho=40, largo=30)  # usa tus valores reales
    tablero.initialization_simulation()

    viz = Visualizer(tablero)
    
    #Prueba por consola para revisar que los vehiculos se meuven
    #tablero.start_simulation()
    viz.run()
    """
    # Inicialización del tablero y visualizador
    tablero = Tablero(ancho=40, largo=35) 
    # Asegúrate de que initialization_simulation() y set_sim_state() existen en Tablero
    #tablero.initialization_simulation() 
    #tablero.set_sim_state("paused") 
    
    viz = Visualizer(tablero)
    #tablero.initialization_simulation()  #Lo comento para que el boton init inicialice todo, o de última lo cambiamos para que se inicialicen solo los vehiculos
    tablero.actualizar_matriz()                   
    tablero._guardar_estado_en_historial()        
    tablero.set_sim_state("paused")

    
    
    replay = ReplayManager()
    viz.replay_manager = replay
    tick = 0    
    replay_file = os.path.join(replay.save_dir, "partida_actual.pkl")

    pos_guardada = 0
    ruta_pos = os.path.join(replay.save_dir, "posicion_replay.txt")
    if os.path.exists(replay_file):
        frames = replay.cargar_pickle("partida_actual.pkl")
        total = len(frames)
        pos_guardada = 0

        # Leer último frame visto
        if os.path.exists(ruta_pos):
            with open(ruta_pos) as f:
                try:
                    pos_guardada = int(f.read().strip())
                except ValueError:
                    pos_guardada = 0

        # Si hay frames guardados
        if total > 0:
            pos_guardada = min(pos_guardada, total - 1)
            ultimo_tablero = modo_replay_misma_pantalla(viz, replay, auto_play=False, desde_frame=pos_guardada)
            if total < 60:
                print(f"[INFO] Replay incompleto ({total}/60 frames). Reanudando simulación...")
                tablero.copiar_estado_de(ultimo_tablero)
                tablero.set_sim_state("running")
                tick = total
                
            
    TIEMPO_PASO_MS = 1000 # Reducido a 200ms para que el movimiento sea visible
    ultimo_paso_tiempo = pygame.time.get_ticks()
    
    prev_state = tablero.sim_state
    menu_shown = False
    
    # 3) loop de visualización
    running = True
    while running:
        tiempo_actual = pygame.time.get_ticks()
        
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
                replay.guardar_pickle("partida_actual.pkl")
                with open(ruta_pos, "w") as f:
                    f.write(str(tick))
            # --- MANEJO CENTRALIZADO DE EVENTOS ---
            # Si el evento es un clic o una tecla, el Visualizer lo procesa.
            
            # 1. Manejo de clics/botones (MOUSEDOWN/MOUSEUP)
            if e.type == pygame.MOUSEBUTTONUP and e.button == 1:
                # Esta línea debe llamar al método del Visualizer que procesa los clics
                viz.handle_button_click(e)           
                replay.registrar_frame(tablero, tick)
                tick += 1
            
            # 2. Manejo de teclas
            if e.type == pygame.KEYDOWN:
                # A. Botón SPACE para Play/Pause
                if e.key == pygame.K_SPACE:
                    viz._do_play_pause() # Llama directamente al método que alterna el estado

                # B. Teclas de Replay (<< y >>)
                elif e.key == pygame.K_LEFT:
                    viz._do_prev()
                elif e.key == pygame.K_RIGHT:
                    viz._do_next()
                    
                # C. Teclas de Debug (R y V)
                elif e.key == pygame.K_r:
                    tablero.inicializar_elementos_aleatoriamente()
                    tablero.actualizar_matriz()
                    tablero._guardar_estado_en_historial()
                elif e.key == pygame.K_v:
                    tablero.inicializar_vehiculos()
                    tablero.actualizar_matriz()
                    tablero._guardar_estado_en_historial()
                    
        # --- Lógica de la Simulación (Tick Controlado) ---
        if tablero.sim_state == "running":
            # Avanza el juego si ha pasado el tiempo definido (200ms)
            if tiempo_actual - ultimo_paso_tiempo >= TIEMPO_PASO_MS:
                tablero.ejecutar_un_paso_simulacion() 
                ultimo_paso_tiempo = tiempo_actual
                replay.registrar_frame(tablero, tick)
                tick += 1
        
        if tablero.sim_state == "running":
            now = pygame.time.get_ticks()
            # primera referencia
            if not hasattr(viz, "_last_timer_tick"):
                viz._last_timer_tick = now
            # ¿pasó 1 segundo?
            if now - viz._last_timer_tick >= 1000:
                viz.timer_seconds = max(0, viz.timer_seconds - 1)
                viz._last_timer_tick = now

                # si llegó a 0 → detener (el menú lo abre el bloque de 'stopped')
                if viz.timer_seconds <= 0:
                    viz.timer_seconds = 0
                    pygame.display.flip()
                    pygame.time.delay(500)
                    try:
                        tablero.set_sim_state("stopped")
                    except Exception as e:
                        print("Error al detener por tiempo agotado:", e)

        # --- Dibujar frame ---
        viz.pantalla.fill(viz.color_fondo)
        viz.draw_grid()
        viz.draw_buttons() # Dibuja los botones (se encarga del hover/press)
        viz.draw_mine_radius()
        viz.draw_from_tablero()
        viz.draw_vehicles() 
        pygame.display.flip()
        viz.clock.tick(60)
        
            # --- Detectar fin de simulación y abrir menú una sola vez ---
        if (not menu_shown) and prev_state != "stopped" and tablero.sim_state == "stopped":
            try:
                replay.guardar_pickle("partida_actual.pkl")
            except Exception:
                pass

            from data.simulations.gui_replay import mostrar_menu_final
            mostrar_menu_final(viz, replay)

            menu_shown = True
            running = False  # (si querés salir del bucle después del menú)

        prev_state = tablero.sim_state

    if tablero.sim_state == "stopped":
        running = False
        replay.guardar_pickle("partida_actual.pkl")
        mostrar_menu_final(viz, replay)
        #pygame.init()
        # Creamos un nuevo visualizador para restaurar la ventana
        #viz = Visualizer(tablero, ancho=viz_ancho, alto=viz_alto)
    #viz.clock.tick(60)
        
        
    pygame.quit()    
    


if __name__ == "__main__":
    main()