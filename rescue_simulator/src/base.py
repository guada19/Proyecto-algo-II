from config.strategies import player1_strategies, player2_strategies

class Base():
    def __init__(self, ancho, largo, jugador, vehiculos):
        self.ancho = ancho
        self.largo = largo
        self.puntaje = 0
        self.jugador = jugador
        self.vehiculos = vehiculos
        self.estrategia = None
    
    def mostrar_puntaje(self):
        print(f"El puntaje del jugador: {self.jugador} es de: {self.puntaje}")
    
    def entregar_recursos(self, vehiculo):
        """Descarga los recursos del vehículo y suma los puntos."""
        pass
    
    #Agrego esta funcionalidad para comunicar la base de cada jugador a la estrategia de cada uno
    def asignar_estrategia(self, estrategia):
        self.estrategia = estrategia