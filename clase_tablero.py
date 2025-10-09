from clase_vehiculo import *

class Tablero:
    def __init__(self, ancho, largo):
        self.ancho = ancho
        self.largo = largo
        self.matriz = [["0" for _ in range(ancho)] for _ in range(largo)]
        self.vehiculos = []

    def inicializar_vehiculos(self, ancho):
        
        Jeep.filas_por_jugador = {1: 0, 2: 0}
        Moto.filas_por_jugador = {1: 0, 2: 0}
        Camion.filas_por_jugador = {1: 0, 2: 0}
        Auto.filas_por_jugador = {1: 0, 2: 0}

        
        vehiculos_jugador1 = [Jeep(0, 1) for _ in range(3)] + \
                                  [Moto(0, 1) for _ in range(2)] + \
                                  [Camion(0, 1) for _ in range(2)] + \
                                  [Auto(0, 1) for _ in range(3)]

        
        vehiculos_jugador2 = [Jeep(ancho-1, 2) for _ in range(3)] + \
                                  [Moto(ancho-1, 2) for _ in range(2)] + \
                                  [Camion(ancho-1, 2) for _ in range(2)] + \
                                  [Auto(ancho-1, 2) for _ in range(3)]
        
        self.vehiculos = vehiculos_jugador1 + vehiculos_jugador2
        
        # Poner los vehículos en la matriz
        self.actualizar_matriz()

    def actualizar_matriz(self):
        # Limpiar la matriz
        self.matriz = [["0" for _ in range(self.ancho)] for _ in range(self.largo)]

        for v in self.vehiculos:
            x, y = v.posicion
            self.matriz[x][y] = v.tipo[0]
            
    def ejecutar_turno_global(self):
        for v in self.vehiculos:
            v.posicion_anterior = (v.x, v.y)  
            v.ejecutar_estrategia()          

        
        self.actualizar_matriz_parcial()

    def actualizar_matriz_parcial(self):
        for v in self.vehiculos:
            x_ant, y_ant = v.posicion_anterior
            self.matriz[x_ant][y_ant] = "0"
        for v in self.vehiculos:
            x, y = v.posicion
            self.matriz[x][y] = v.tipo[0]

    def mostrar_tablero(self):
        for fila in self.matriz:
            print(" ".join(f"[{celda}]" for celda in fila))
