class Vehiculo:
    
    filas_por_jugador = {1: 0, 2: 0}
    
    def __init__(self, tipo, posicion, capacidad_carga, viajes_restantes, tipo_carga_permitida, estado, jugador, max_viajes):
        self.tipo = tipo
        self.x, self.y = Vehiculo.filas_por_jugador[jugador], posicion
        Vehiculo.filas_por_jugador[jugador] += 1
        self.capacidad_carga = capacidad_carga
        self.viajes_restantes = viajes_restantes
        self.tipo_carga_permitida = tipo_carga_permitida
        self.estado = estado
        self.jugador = jugador
        self.max_viajes = max_viajes
    
    @property
    def posicion(self):
        #retornar la posición como tupla
        return (self.x, self.y)
    
    def mover(self):
        pass
    def agarrar_recurso(self):
        pass
    
    def volver_a_la_base(self):
        pass
    
    def detectar_colision(self):
        pass
    
    def destruir(self):
        #Marca el vehículo como destruido.
        self.estado = "destruido"

    def ejecutar_estrategia(self):
        if self.estado == "activo": 
            self.x += 1
            if self.y == 0:
                self.y +=1
            elif self.y == 15:
                self.y -= 1
    

class Jeep(Vehiculo):
    def __init__(self, posicion, jugador):
        super().__init__(tipo = "Jeep", posicion = posicion, capacidad_carga = 2, viajes_restantes = 2, tipo_carga_permitida = ["persona", "mercancia"], estado = "activo", jugador = jugador, max_viajes = 2)

class Moto(Vehiculo):
    def __init__(self, posicion,jugador):
        super().__init__(tipo = "Moto", posicion = posicion, capacidad_carga = 1, viajes_restantes = 1, tipo_carga_permitida = "persona", estado = "activo", jugador = jugador, max_viajes = 1)

class Camion(Vehiculo):
    def __init__(self, posicion, jugador):
        super().__init__(tipo = "Camion", posicion = posicion, capacidad_carga = 3, viajes_restantes = 3, tipo_carga_permitida = ["persona", "mercancia"], estado = "activo", jugador = jugador, max_viajes = 3)
   
class Auto(Vehiculo):
    def __init__(self, posicion, jugador):
        super().__init__(tipo = "Auto", posicion = posicion, capacidad_carga = 1, viajes_restantes = 1, tipo_carga_permitida = ["persona", "mercancia"], estado = "activo", jugador = jugador, max_viajes = 1) 
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        