class Mine():
    def __init__(self, posicion, estado, radio, estatica):
        self.x, self.y = posicion
        self.estado = estado
        self.radio = radio
        self.estatica = estatica
    
    @property
    def posicion(self):
        return (self.x, self.y)
    
    def explotar(self):
        pass

class MinesCircularesEstaticas(Mine):
    def __init__(self, posicion, tipo):
        self.tipo = tipo # 1 para O1, 2 para O2
        radio = 10 if self.tipo == 1 else 5 
        super().__init__(posicion=posicion, estado="activo", radio=radio, estatica=True)
    
class MinesLinealesEstaticas(Mine):
    def __init__(self, posicion, tipo): # Recibe el tipo: 1 para "T1" o 2 para "T2"
        
        self.orientacion = "horizontal" if tipo == 1 else "vertical"
        radio = 10 if tipo == 1 else 5
        
        super().__init__(posicion = posicion, estado = "activo", radio = radio , estatica = True)
        
class MineG1(Mine):
    def __init__(self, posicion):
        super().__init__(posicion, estado = "activa", radio = 7, estatica = False)
        self.contador_de_tiempo = 5
    
    def actualizar_estado(self):
        pass