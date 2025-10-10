from clase_vehiculo import *

class Tablero:
    def __init__(self, ancho, largo):
        self.ancho = ancho
        self.largo = largo
        self.matriz = [["0" for _ in range(ancho)] for _ in range(largo)]
        self.vehiculos = []
        self.recursos = []
        
    def inicializar_vehiculos(self):
        tipos = [
            (Jeep, 3),
            (Moto, 2),
            (Camion, 2),
            (Auto, 3)
        ]

        self.vehiculos = []
        Vehiculo.filas_por_jugador = {1: 0, 2: 0}

        for clase, cantidad in tipos:
            for jugador in (1, 2):
                for _ in range(cantidad):
                    if jugador == 1:
                        x = Vehiculo.filas_por_jugador[1]
                        y = 0
                        Vehiculo.filas_por_jugador[1] += 1
                    else:
                        x = self.largo - 1 - Vehiculo.filas_por_jugador[2]
                        y = self.ancho-1
                        Vehiculo.filas_por_jugador[2] += 1

                    self.vehiculos.append(clase(posicion=(x, y), jugador=jugador))

        self.actualizar_matriz()

    def actualizar_matriz(self):
        self.matriz = [["0" for _ in range(self.ancho)] for _ in range(self.largo)]
        for v in self.vehiculos:
            x, y = v.posicion
            if 0 <= x < self.ancho and 0 <= y < self.largo:
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
