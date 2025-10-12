from src.map_manager import Tablero
from src.visualization import Visualizer

def main():
    tablero = Tablero(ancho=50, largo=50)  # usa tus valores reales
    viz = Visualizer(tablero)
    viz.run()


if __name__ == "__main__":
    main()