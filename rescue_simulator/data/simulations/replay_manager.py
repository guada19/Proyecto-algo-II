import pickle
import json
import os
import copy

class ReplayManager:
    def __init__(self, save_dir="replays"):
        self.historial_frames = []
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)

    def registrar_frame(self, tablero, tick):
        
        tablero_copia = copy.deepcopy(tablero)
        frame_data = {
            "tick": tick,
            "tablero": tablero_copia
        }
        self.historial_frames.append(frame_data)
        
    def guardar_pickle(self, nombre="replay.pkl"):
        """
        Guarda todo el historial en formato pickle (rápido y nativo).
        """
        ruta = os.path.join(self.save_dir, nombre)
        with open(ruta, "wb") as f:
            pickle.dump(self.historial_frames, f)

    def guardar_json_resumido(self, nombre="replay.json"):
        """
        Guarda una versión resumida en JSON (solo posiciones y ticks).
        Ajustado para acceder a los datos a través del objeto Tablero.
        """
        ruta = os.path.join(self.save_dir, nombre)
        
        # Iteramos sobre el historial
        data = [
            {
                "tick": frame["tick"],
                # ACCESO CORREGIDO: 
                # Ahora accedemos a .tablero.vehiculos y obtenemos la posición.
                # NOTA: Asume que frame["tablero"].vehiculos es una lista de objetos
                #       donde cada objeto tiene una propiedad 'posicion' o 'pos'.
                "vehiculos": [v.posicion for v in frame["tablero"].vehiculos], # Usamos .posicion (o .pos, verifica tu clase Vehiculo)
                
                # Para recursos, asumiendo que están en .tablero.recursos
                "recursos": [r.posicion for r in getattr(frame["tablero"], "recursos", []) if hasattr(r, "posicion")],
            }
            for frame in self.historial_frames
        ]
        with open(ruta, "w") as f:
            json.dump(data, f, indent=2)
            
    def cargar_pickle(self, nombre="replay.pkl"):
        """
        Carga un replay previamente guardado.
        """
        ruta = os.path.join(self.save_dir, nombre)
        with open(ruta, "rb") as f:
            self.historial_frames = pickle.load(f)
        return self.historial_frames
