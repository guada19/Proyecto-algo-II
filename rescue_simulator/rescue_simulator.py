import pygame
from src.map_manager import Tablero
from src.visualization import Visualizer
from data.simulations.replay_manager import ReplayManager


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
    tick = 0    

    # Temporizador de la simulación
    TIEMPO_PASO_MS = 1000 # Reducido a 200ms para que el movimiento sea visible
    ultimo_paso_tiempo = pygame.time.get_ticks()
    
    
    # 3) loop de visualización
    running = True
    while running:
        tiempo_actual = pygame.time.get_ticks()
        
        tiempo_actual = pygame.time.get_ticks()
        
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            
            # --- MANEJO CENTRALIZADO DE EVENTOS ---
            # Si el evento es un clic o una tecla, el Visualizer lo procesa.
            
            # 1. Manejo de clics/botones (MOUSEDOWN/MOUSEUP)
            if e.type == pygame.MOUSEBUTTONUP and e.button == 1:
                 # Esta línea debe llamar al método del Visualizer que procesa los clics
                 viz.handle_button_click(e) 
            
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
        
        # --- Dibujar frame ---
        viz.pantalla.fill(viz.color_fondo)
        viz.draw_grid()
        viz.draw_buttons() # Dibuja los botones (se encarga del hover/press)
        viz.draw_mine_radius()
        viz.draw_from_tablero() 
        pygame.display.flip()
        viz.clock.tick(60)

    replay.guardar_pickle("partida_actual.pkl")
    replay.guardar_json_resumido("partida_actual.json")  

    pygame.quit()  
    
        
        #viz.clock.tick(60)
        
        
    pygame.quit()    
    

if __name__ == "__main__":
    main()