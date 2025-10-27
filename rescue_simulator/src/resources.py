class Resource():
    def __init__(self, posicion, puntaje, estado, categoria):
        self.x, self.y = posicion
        self.puntaje = puntaje
        self.estado = estado 
        self.categoria = categoria
        self.asignado_a = None
    
    def recolectado(self):
        self.estado = "recolectado"
     
    def destruirse(self):
        self.estado = "destruido"
        
class Person(Resource):
    def __init__(self):
        super().__init__(posicion = (0,0), puntaje = 50, estado = "disponible", categoria = "persona")


class Mercancia(Resource):
    def __init__(self, posicion, subtipo, puntaje):
        super().__init__(posicion = posicion, puntaje = puntaje, estado = "disponible", categoria = "mercancia")
        self.subtipo = subtipo 
        
class Alimento(Mercancia):
    def __init__(self):
        super().__init__(posicion = (0,0), subtipo = "comida", puntaje = 10)

class Ropa(Mercancia):
    def __init__(self):
        super().__init__(posicion = (0,0), subtipo = "ropa", puntaje = 5)

class Medicamento(Mercancia):
    def __init__(self):
        super().__init__(posicion = (0,0), subtipo = "medicamento", puntaje = 20)

class Armamento(Mercancia):
    def __init__(self):
        super().__init__(posicion = (0,0), subtipo = "armamento", puntaje = 50)