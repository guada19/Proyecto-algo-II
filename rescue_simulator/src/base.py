class Base():
    def __init__(self, ancho, largo, jugador, vehiculos):
        self.ancho = ancho
        self.largo = largo
        self.puntaje = 0
        self.jugador = jugador
        self.vehiculos = vehiculos
    
    def mostrar_puntaje(self):
        print(f"El puntaje del jugador: {self.jugador} es de: {self.puntaje}")
    
    def entregar_recursos(self, vehiculo):
        """Descarga los recursos del vehículo y suma los puntos."""
        pass