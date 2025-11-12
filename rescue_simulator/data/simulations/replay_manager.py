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

    def cargar_pickle(self, nombre="replay.pkl"):
        """
        Carga un replay previamente guardado.
        """
        ruta = os.path.join(self.save_dir, nombre)
        with open(ruta, "rb") as f:
            self.historial_frames = pickle.load(f)
        return self.historial_frames
    
    def reset(self):
        """Vacía los frames en memoria y elimina los archivos guardados."""
        self.historial_frames.clear()
        for nombre in ["partida_actual.pkl", "posicion_replay.txt"]:
            ruta = os.path.join(self.save_dir, nombre)
            if os.path.exists(ruta):
                os.remove(ruta)