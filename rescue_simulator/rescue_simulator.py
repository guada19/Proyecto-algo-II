from src.visualization import Visualizer

def main():
    viz = Visualizer(ancho=1080, alto=720, tamaño_celdas=20)
    viz.run()

if __name__ == "__main__":
    main()
