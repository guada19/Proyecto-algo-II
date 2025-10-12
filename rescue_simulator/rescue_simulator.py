from src.map_manager import Tablero
from src.visualization import Visualizer

def main():
    tablero = Tablero(ancho=50, largo=50)  # usa tus valores reales
    
    tablero.inicializar_vehiculos()

    # Crear un par de recursos y minas
    from src.resources import Resource
    from src.mines import Mine

    tablero.recursos = [
        Resource((5, 10), 10, "disponible", "mercancia"),
        Resource((12, 15), 10, "disponible", "persona"),
    ]
    tablero.minas = [
        Mine((8, 20), "activa", 3, True),
        Mine((14, 25), "activa", 3, True),
    ]
    tablero.actualizar_matriz()
    viz = Visualizer(tablero)
    viz.run()


if __name__ == "__main__":
    main()