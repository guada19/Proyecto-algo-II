# Rescue Simulator — Proyecto Algoritmos II

**Tecnologías**: Python 3.10+, Pygame

Rescue Simulator es una simulación por turnos donde dos jugadores (J1 y J2) compiten por rescatar personas y recolectar mercancías evitando minas. Incluye estrategias diferentes por jugador, pathfinding híbrido y modo de repetición.

---

## Cómo ejecutar

1. Crear y activar venv (opcional, recomendado):
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```
2. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```
3. Ejecutar:
   ```bash
   python rescue_simulator.py
   ```
---

## Controles rápidos

- **init**: inicializa el tablero con vehículos, recursos y minas.
- **play / pause**: inicia o pausa la simulación.
- **stop**: finaliza la simulación (muestra menú final / replay).
- **<< prev / next >>**: navegación cuadro a cuadro del **replay** en pausa.
- **ESC / Cerrar ventana**: sale del programa (guarda replay actual).

Atajos teclado replay:
- `ESPACIO`: play/pause
- `← / →`: prev / next
- `ESC`: salir

---

## Reglas del juego (resumen)

- Vehículos: **Moto**, **Auto**, **Jeep**, **Camión**.
- Cada vehículo tiene **capacidad** y **máx. de viajes** (si tu versión lo incluye):
  - Moto: 1 (solo personas) — 1 viaje
  - Auto: 1 (personas/mercancías) — 1 viaje
  - Jeep: 2 (personas/mercancías) — 2 viajes
  - Camión: 3 (personas/mercancías) — 3 viajes
- Las **entregas** se realizan al regresar a la base propia.
- Puntajes por mercancía (subtipo):
  - alimento: 10 
  - ropa: 5
  - medicamento: 20
  - armamento: 50

---

## Estrategias y Pathfinding

- **Jugador 1 (J1)**: objetivo por **BFS** y navegación inicial **BFS**, retorno a base con **A***.
- **Jugador 2 (J2)**: selección de objetivo por **Dijkstra** y navegación **A***.

---

## Arquitectura (resumen)

- `src/map_manager.py` — motor de simulación, tablero, estados, puntaje, historial.
- `src/visualization.py` — UI Pygame, botones y dibujo del tablero.
- `src/aircraft.py` — clases de vehículos y utilidades.
- `src/player1_strategies.py` / `src/player2_strategies.py` — comportamientos por jugador.
- `src/pathfinding.py` — BFS / Dijkstra / A*.
- `data/simulations/` — administración de **replay**.

---

## Pruebas manuales sugeridas

1. **Inicialización**: `init` → aparecen recursos, minas y vehículos en sus filas.
2. **Movimiento**: `play` → unidades salen, recolectan y entregan.
3. **Puntaje**: al entregar aumenta el marcador de J1/J2.
4. **Replay**: `stop` → se muestra menú y se puede ver la repetición, usar prev/next.
5. **Colisiones**: verificar que se registren y no rompan el flujo.
6. **Minas G1**: validar parpadeo/visibilidad según regla establecida.

---

## Estructura de carpetas (recomendada)

```
.
├─ rescue_simulator.py
├─ src/
│  ├─ map_manager.py
│  ├─ visualization.py
│  ├─ pathfinding.py
│  ├─ aircraft.py
│  ├─ player1_strategies.py
│  └─ player2_strategies.py
├─ data/
│  ├─ images/
│  └─ simulations/
├─ docs/
├─ requirements.txt
└─ README.md

## Requisitos de entorno

- Python 3.10 o superior
- Pygame
- SO: Windows

---

## Integrantes

- Guadalupe Nadal
- Andrea Pereyra 

Repositorio: [(https://github.com/guada19/Proyecto-algo-II.git)]

