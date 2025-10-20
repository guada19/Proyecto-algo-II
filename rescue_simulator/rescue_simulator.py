import pygame
from src.map_manager import Tablero
from src.visualization import Visualizer

def main():
    # Inicialización del tablero y visualizador
    tablero = Tablero(ancho=50, largo=50)  # usa tus valores reales
    viz = Visualizer(tablero)
    
    # Temporizador de la simulación (Regla 6: 2 segundos por movimiento)
    TIEMPO_PASO_MS = 2000 # 2 segundos
    ultimo_paso_tiempo = pygame.time.get_ticks()

    # 3) loop de visualización
    running = True
    while running:
        tiempo_actual = pygame.time.get_ticks()
        
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            
            # Manejo de clics en los botones de la interfaz (Regla 1, 2, 7, 8, 9, 10)
            for btn in viz.buttons:
                btn.handle_event(e)
            
            # Manejo de teclas existentes (mantener por si acaso)
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r:
                    # regenerar mapa: recursos/minas nuevas
                    tablero.inicializar_elementos_aleatoriamente()
                    tablero.actualizar_matriz()
                    tablero._guardar_estado_en_historial() # Guardar el estado inicial
                elif e.key == pygame.K_v:
                    # re-spawn de vehículos (opcional)
                    tablero.inicializar_vehiculos()
                    tablero.actualizar_matriz()
                    tablero._guardar_estado_en_historial() # Guardar el estado inicial
                # Teclas de paso a paso opcionales
                elif e.key == pygame.K_LEFT:
                    tablero.prev_frame()
                elif e.key == pygame.K_RIGHT:
                    tablero.next_frame()


        # --- Lógica de la Simulación ---
        if tablero.sim_state == "running":
            if tiempo_actual - ultimo_paso_tiempo >= TIEMPO_PASO_MS:
                tablero.ejecutar_un_paso_simulacion() # Ejecuta el movimiento (Regla 6)
                ultimo_paso_tiempo = tiempo_actual
        
        # --- Dibujar frame ---
        viz.pantalla.fill(viz.color_fondo)
        viz.draw_grid()
        viz.draw_buttons() # Dibuja los botones
        viz.draw_from_tablero()    # ← pinta R/X/J/M/C/A según la matriz actual del historial
        pygame.display.flip()
        viz.clock.tick(60)

    pygame.quit()  
    
if __name__ == "__main__":
    main()