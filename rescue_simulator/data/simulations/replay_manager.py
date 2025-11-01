import pickle
import json
import os

class ReplayManager:
    def __init__(self, save_dir="replays"):
        self.historial_frames = []
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)

    def registrar_frame(self, tablero, tick):
        """
        Guarda el estado actual del tablero en el historial de la simulación.
        """
        frame_data = {
            "tick": tick,
            "vehiculos": [
                {
                    "tipo": type(v).__name__,
                    "pos": v.posicion,
                    "estado": v.estado,
                    "carga_actual": len(getattr(v, "carga_actual", []))
                }
                for v in tablero.vehiculos
            ],
            "recursos": [
                {
                    "pos": getattr(r, "posicion", getattr(r, "pos", None)),
                    "estado": getattr(r, "estado", None),
                    "categoria": getattr(r, "categoria", None),
                    "tipo": type(r).__name__,
                }
                for r in getattr(tablero, "recursos", [])
                if hasattr(r, "posicion") or hasattr(r, "pos")
            ]
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
        """
        ruta = os.path.join(self.save_dir, nombre)
        data = [
            {
                "tick": frame["tick"],
                "vehiculos": [v["pos"] for v in frame["vehiculos"]],
                "recursos": [r["pos"] for r in frame["recursos"]],
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