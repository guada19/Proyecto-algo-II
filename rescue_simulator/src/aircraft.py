import random

class Vehiculo:
    
    filas_por_jugador = {1: 0, 2: 0}
    
    def __init__(self, tipo, posicion, capacidad_carga, viajes_restantes, tipo_carga_permitida, estado, jugador, max_viajes):
        self.tipo = tipo
        self.x, self.y = posicion
        self.posicion_anterior = self.posicion
        self.capacidad_carga = capacidad_carga
        self.viajes_restantes = viajes_restantes
        self.tipo_carga_permitida = tipo_carga_permitida
        self.estado = estado
        self.jugador = jugador
        self.max_viajes = max_viajes
        self.carga_actual = []
        self.estrategia = None                  
        self.camino_restante = []               
        self.posicion_intencionada = self.posicion
        self.objetivo_recurso = None
    
    
    @property
    def posicion(self):
        #retornar la posición como tupla
        return (self.x, self.y)
    
    @posicion.setter
        #propiedad que permite cambiarle la posición al veículo
    def posicion(self, nueva_pos):
        self.x, self.y = nueva_pos
    
    def mover(self, pos_final):
        self.posicion_anterior = self.posicion
        self.posicion = pos_final
    
    def agarrar_recurso(self, tablero):
        
        recurso = tablero.pos_recursos.get(self.posicion)
        
        if recurso and recurso.estado == "disponible":
            if (recurso.categoria in self.tipo_carga_permitida) and len(self.carga_actual) < self.capacidad_carga:
                self.carga_actual.append(recurso)
                recurso.recolectado()
                self.viajes_restantes -= 1
                del tablero.pos_recursos[self.posicion]
                print(f"{self.tipo} del jugador {self.jugador} recogió {recurso.categoria} en {self.posicion}")
                self.objetivo_recurso = None
                self.camino_restante = []
                return True
            
        return False
            
    def volver_a_la_base(self, tablero):
        pass
    
    
    def detectar_colision(self):
        pass
    
    def destruir(self):
        #Marca el vehículo como destruido.
        self.estado = "destruido"
        self.x, self.y = -1, -1 
        self.posicion_intencionada = (-1, -1)
        self.destruir_carga() 
    
    def destruir_carga(self):
        for carga in self.carga_actual:
            carga.destruirse()   
    
    """
    Esta funcion ya no la veo como útil porque la estrategia está en cada uno de los jugadores
    así que los vehiculos no ejecutan una estrategia sino que se mueven como el jugador pensó la estrategia
        def ejecutar_estrategia(self):
        #Acá habría que relacionarlo con la clase jugador accediendo a self.jugador
        #y que cada vehículo tenga su propio método con un @override
        #Por ahora es un método abstracto
        pass
    
    """

class Jeep(Vehiculo):
    def __init__(self, posicion, jugador):
        super().__init__(tipo = "Jeep", posicion = posicion, capacidad_carga = 2, viajes_restantes = 2, tipo_carga_permitida = ["persona", "mercancia"], estado = "activo", jugador = jugador, max_viajes = 2)
    
class Moto(Vehiculo):
    def __init__(self, posicion,jugador):
        super().__init__(tipo = "Moto", posicion = posicion, capacidad_carga = 1, viajes_restantes = 1, tipo_carga_permitida = ["persona"], estado = "activo", jugador = jugador, max_viajes = 1)

class Camion(Vehiculo):
    def __init__(self, posicion, jugador):
        super().__init__(tipo = "Camion", posicion = posicion, capacidad_carga = 3, viajes_restantes = 3, tipo_carga_permitida = ["persona", "mercancia"], estado = "activo", jugador = jugador, max_viajes = 3)
    
class Auto(Vehiculo):
    def __init__(self, posicion, jugador):
        super().__init__(tipo = "Auto", posicion = posicion, capacidad_carga = 1, viajes_restantes = 1, tipo_carga_permitida = ["persona", "mercancia"], estado = "activo", jugador = jugador, max_viajes = 1)