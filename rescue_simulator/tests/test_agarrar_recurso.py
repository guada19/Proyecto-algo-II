import sys
import os

# Añade el directorio principal (../) al PYTHONPATH.
# Esto permite importar módulos como 'src.map_manager'.
#Basicamente le dice al archivo que debe buscar los módulos por fuera de la carpeta test y que busque en toda la carpeta de rescue_simulator
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))





from src.map_manager import Tablero 
from src.aircraft import Moto 
from src.resources import Person 


def test_recoleccion_manual():
    """Prueba que la recolección funciona, verifica carga, estado y limpieza del mapa."""
    
    # ... (Tu código de SETUP) ...
        # --- 1. SETUP MANUAL: CREAR ESCENARIO DE COLISIÓN ---
    
    # 1.1 Definir la posición de colisión (Manual "Movimiento")
    posicion_colision = (3, 8)
    
    # 1.2 Crear Tablero, Vehículo y Recurso
    tablero = Tablero(ancho=10, largo=10)
    persona = Person() 
    moto = Moto(posicion=posicion_colision, jugador=1) # Moto creada en (3, 8)
    
    # 1.3 Asignar posiciones manuales
    # Esto simula que la Moto se ha "movido" a (3, 8) y que la Persona está allí.
    persona.x, persona.y = posicion_colision 
    
    # 1.4 Configurar el diccionario (O(1))
    # Esto simula que el recurso está en el mapa, listo para ser encontrado.
    tablero.pos_recursos = {posicion_colision: persona} # Usar el nombre de tu diccionario

    # Estado inicial para depuración
    print(f"SETUP: Posición de Vehículo y Recurso: {moto.posicion}")
    print(f"SETUP: Recurso en mapa? {posicion_colision in tablero.pos_recursos}")
    print(f"SETUP: Carga inicial de Moto: {len(moto.carga_actual)}")
    # --- DEBUGGING CRÍTICO ---
    print("-" * 30)
    print(f"DEBUGGING: Atributos Críticos de Moto y Persona")
    
    # Valores de la MOTO (¡DEBEN ser correctos!)
    print(f"1. Capacidad Máxima (self.capacidad_carga): {moto.capacidad_carga}") 
    print(f"2. Tipos Permitidos (self.tipo_carga_permitida): {moto.tipo_carga_permitida}") 
    
    # Valores de la PERSONA (¡DEBEN ser correctos!)
    print(f"3. Categoría del Recurso (recurso.categoria): {persona.categoria}") 
    print(f"4. Estado del Recurso (recurso.estado): {persona.estado}") 
    print("-" * 30)
    print("\n--- INICIANDO PRUEBA MANUAL DE RECOLECCIÓN ---")


    
    # --- 2. ACCIÓN: EJECUTAR FUNCIÓN A PROBAR ---
    
    recoleccion_exitosa = moto.agarrar_recurso(tablero)
    
    # --- 3. VERIFICACIÓN MANUAL (ASSERTIONS) ---
    
    print("\nRESULTADO:")
    
    # V-1: La función debe indicar éxito
    assert recoleccion_exitosa is True
    print(f" - V-1 (Retorno): Éxito. recoleccion_exitosa = {recoleccion_exitosa}")
    
    # V-2: La Moto debe tener el recurso cargado (carga_actual debe ser 1)
    assert len(moto.carga_actual) == 1
    assert moto.carga_actual[0] is persona
    print(f" - V-2 (Carga Moto): {len(moto.carga_actual)} (Correcto)")
    
    # V-3: El recurso debe cambiar su estado interno (ya no está disponible)
    assert persona.estado == "recolectado"
    print(f" - V-3 (Estado Recurso): '{persona.estado}' (Correcto)")
    
    # V-4: El recurso debe ser eliminado del diccionario del Tablero
    assert posicion_colision not in tablero.pos_recursos
    print(f" - V-4 (Limpieza Mapa O(1)): Recurso removido (Correcto)")
    
    print("\n--- PRUEBA DE RECOLECCIÓN MANUAL: PASADA ---")

# Ejecutar la prueba
if __name__ == "__main__":
    test_recoleccion_manual() 