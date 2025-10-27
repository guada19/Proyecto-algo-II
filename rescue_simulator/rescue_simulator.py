import pygame
from src.map_manager import Tablero
from src.visualization import Visualizer


def main():
    tablero = Tablero(ancho=40, largo=30)  # usa tus valores reales
    tablero.initialization_simulation()

    viz = Visualizer(tablero)
    
    #Prueba por consola para revisar que los vehiculos se meuven
    #tablero.start_simulation()
    viz.run()
    
    

if __name__ == "__main__":
    main()


