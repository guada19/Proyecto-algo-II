class Resource():
    def __init__(self, posicion, puntaje, estado, categoria):
        self.x, self.y = posicion
        self.puntaje = puntaje
        self.estado = estado 
        self.categoria = categoria
    
    def recolectado(self):
        self.estado = "recolectado"
     
    def destruirse(self):
        self.estado = "destruido"
        
class Person(Resource):
    def __init__(self, posicion):
        super().__init__(posicion, puntaje = 50, estado = "disponible", categoria = "persona")


class Mercancia(Resource):
    def __init__(self, posicion, subtipo, puntaje):
        super().__init__(posicion, puntaje = puntaje, estado = "disponible", categoria = "mercancia")
        self.subtipo = subtipo 
        
class Alimento(Mercancia):
    def __init__(self, posicion):
        super().__init__(posicion, subtipo = "alimento", puntaje = 10)

class Ropa(Mercancia):
    def __init__(self, posicion):
        super().__init__(posicion, subtipo = "ropa", puntaje = 5)

class Medicamento(Mercancia):
    def __init__(self, posicion):
        super().__init__(posicion, subtipo = "medicamento", puntaje = 20)

class Armamento(Mercancia):
    def __init__(self, posicion):
        super().__init__(posicion, subtipo = "armamento", puntaje = 50)