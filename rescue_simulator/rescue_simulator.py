import pygame
from src.map_manager import Tablero
from src.visualization import Visualizer


def main():
    tablero = Tablero(ancho=40, largo=30)  # usa tus valores reales
    tablero.initialization_simulation()

    viz = Visualizer(tablero)
    
    # 3) loop de visualización
    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_r:
                    # regenerar mapa: recursos/minas nuevas
                    tablero.inicializar_elementos_aleatoriamente()
                    tablero.actualizar_matriz()
                elif e.key == pygame.K_v:
                    # re-spawn de vehículos (opcional)
                    tablero.inicializar_vehiculos()
                    tablero.actualizar_matriz()

        # dibujar frames
        viz.pantalla.fill(viz.color_fondo)
        viz.draw_grid()
        viz.draw_from_tablero()   # ← pinta R/X/J/M/C/A según matriz
        pygame.display.flip()
        viz.clock.tick(60)

    pygame.quit()    
    
    #Prueba por consola para revisar que los vehiculos se meuven
    tablero.start_simulation()
    #viz.run()
    
    

if __name__ == "__main__":
    main()


