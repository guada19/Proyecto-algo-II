from src.map_manager import Tablero
from src.visualization import Visualizer

def main():
    tablero = Tablero(ancho=50, largo=50)  # usa tus valores reales
    #spawn_en_base_izq(tablero, fila=3, simbolo="J")
    #spawn_en_base_der(tablero, fila=6, simbolo="M")
    viz = Visualizer(tablero)
    viz.run()

#def spawn_en_base_izq(tablero, fila, simbolo="J"):
 #   tablero.matriz[fila][0] = simbolo  # col 0 = base izquierda

#def spawn_en_base_der(tablero, fila, simbolo="M"):
  #  tablero.matriz[fila][tablero.ancho - 1] = simbolo  # col n-1 = base derecha


if __name__ == "__main__":
    main()