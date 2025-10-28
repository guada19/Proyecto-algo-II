import random 
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
        self.estado = "destruida"

class MinesCircularesEstaticas(Mine):
    def __init__(self, tipo):
        self.tipo = "01" if tipo == 1 else "02" # 1 para O1, 2 para O2
        radio = 10 if self.tipo == "01" else 5 
        super().__init__(posicion = (0,0), estado="activa", radio=radio, estatica=True)
    
class MinesLinealesEstaticas(Mine):
    def __init__(self, tipo): # Recibe el tipo: 1 para "T1" o 2 para "T2"
        self.tipo = "T1" if tipo == 1 else "T2"
        self.orientacion = "horizontal" if self.tipo == "T1" else "vertical"
        radio = 10 if self.tipo == "T1" else 5
        
        super().__init__(posicion = (0,0), estado = "activa", radio = radio , estatica = True)
        
class MineG1(Mine):
    def __init__(self):
        super().__init__(posicion = (0,0), estado = "activa", radio = 7, estatica = False)
        self.contador_de_tiempo = 5
        self.tipo = "G1"
    
    def actualizar_estado(self, step_count, tablero): 
        """
        Actualiza el estado y la posición de Mine G1.
        Ciclo: Activa (1-4) -> Desaparece/Mueve (5)
        """
        # El tick actual dentro del ciclo 1-5
        ciclo_tick = (step_count-1) % 5
        
        if self.estado == "destruida":
            return 
            
        if ciclo_tick < 4 and self.estado != "destruida":
            self.estado = "activa"
        else: 
            self.estado = "inactivo"
            
        if ciclo_tick == 4 and self.estado != "destruida":
            self.estado = "inactivo"
            pos_anterior = self.posicion
            posicion_valida = False
            while not posicion_valida:
                
                x = random.randint(0, tablero.largo - 1)
                y = random.randint(1, tablero.ancho - 2) 
                pos = (x, y)
                
                if pos not in tablero.posiciones_ocupadas:
                    
                    self.x, self.y = pos 
                    tablero.posiciones_ocupadas.add(pos)
                    posicion_valida = True
            tablero.posiciones_ocupadas.discard(pos_anterior)