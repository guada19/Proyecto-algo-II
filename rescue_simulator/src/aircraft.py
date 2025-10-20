import random

class Vehiculo:
    
    filas_por_jugador = {1: 0, 2: 0}
    
    def __init__(self, tipo, posicion, capacidad_carga, viajes_restantes, tipo_carga_permitida, estado, jugador, max_viajes):
        self.tipo = tipo
        self.x, self.y = posicion
        self.posicion_anterior = posicion 
        self.capacidad_carga = capacidad_carga
        self.viajes_restantes = viajes_restantes
        self.tipo_carga_permitida = tipo_carga_permitida
        self.estado = estado
        self.jugador = jugador
        self.max_viajes = max_viajes
        self.carga_actual = []
    
    @property
    def posicion(self):
        #retornar la posición como tupla
        return (self.x, self.y)
    
    @property
    def label(self):
        """Retorna la etiqueta del vehículo: Primera letra del tipo + Jugador (Ej: J1, M2)."""
        return f"{self.tipo[0]}{self.jugador}"

    def mover(self):
        pass
    
    def agarrar_recurso(self, tablero):
        
        recurso = tablero.pos_recursos.get(self.posicion)
        
        if recurso and recurso.estado == "disponible":
            if (recurso.categoria in self.tipo_carga_permitida) and len(self.carga_actual) < self.capacidad_carga:
                self.carga_actual.append(recurso)
                recurso.recolectado()
                self.viajes_restantes -= 1
                del tablero.pos_recursos[self.posicion]

                return True
            
        return False
        
    def volver_a_la_base(self):
        pass
    
    def detectar_colision(self):
        pass
    
    def destruir(self):
        #Marca el vehículo como destruido.
        self.estado = "destruido"

    def ejecutar_estrategia(self, tablero):
        """
        Mueve el vehículo aleatoriamente (arriba, abajo, izquierda, derecha) 
        sin volver a la posición anterior y respetando los límites del tablero.
        """
        if self.estado != "activo":  
            return
        
        # Posibles movimientos: (dx, dy)
        movimientos = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        random.shuffle(movimientos) # Aleatoriedad
        
        largo = tablero.largo
        ancho = tablero.ancho
        
        for dx, dy in movimientos:
            nuevo_x = self.x + dx
            nuevo_y = self.y + dy
            nueva_pos = (nuevo_x, nuevo_y)
            
            # Restricción: No puede volver a la posición anterior inmediatamente (evitar vibración)
            if nueva_pos == self.posicion_anterior:
                continue

            # Verificar límites del tablero
            if 0 <= nuevo_x < largo and 0 <= nuevo_y < ancho:
                
                # Regla 5: Restricción de no volver a la base.
                # Si está en la base (col 0 o ancho-1) DEBE salir
                if self.y == 0: 
                    if nuevo_y == 0: continue # No se queda en la base J1
                elif self.y == ancho - 1:
                    if nuevo_y == ancho - 1: continue # No se queda en la base J2
                
                # Si está en el mapa central (1 < y < ancho-2) NO puede volver a la base
                elif 0 < self.y < ancho - 1:
                    if nuevo_y == 0 or nuevo_y == ancho - 1:
                        continue 
                        
                # Si pasa todas las restricciones
                self.posicion_anterior = self.posicion 
                self.x = nuevo_x
                self.y = nuevo_y

                break
        
        # Simulación de recolección de recurso (opcional)
        self.agarrar_recurso(tablero) 


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