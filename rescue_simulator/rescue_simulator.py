from src.map_manager import Tablero
from src.visualization import Visualizer

def main():
    tablero = Tablero(ancho=20, largo=20)  # usa tus valores reales
    viz = Visualizer(tablero)
    viz.run()
    tablero.initialization_simulation()
    
    

if __name__ == "__main__":
    main()


    