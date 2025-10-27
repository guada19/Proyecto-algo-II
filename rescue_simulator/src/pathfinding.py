from queue import PriorityQueue

#Función para verificar si la siguiente celda a la que me quiero mover está vacía
def es_celda_valida(tablero, x, y):
    if 0 <= x < tablero.largo and 0 <= y < tablero.ancho:
        if not tablero.colision_minas(x,y) and not tablero.colision_vehiculos_para_a_star(x,y):
            return True
    return False

#Función para obtener los 4 vecinos posibles desde mi posicion (arriba, abajo, derecha e izquierda)
#sirve para la exploración de un nodo en la función a_star
def get_vecinos(tablero, pos):
    vecinos = []
    x,y = pos
    if es_celda_valida(tablero, x-1, y):
       vecinos.append((x-1, y))
    if es_celda_valida(tablero, x+1, y):
       vecinos.append((x+1, y))
    if es_celda_valida(tablero, x, y-1):
        vecinos.append((x, y-1))
    if es_celda_valida(tablero, x, y+1):
       vecinos.append((x, y+1))
    return vecinos

#funcion que estima la cantidad de moviemiento y la distancia restante hacia el objetivo
def heuristica(a, b):
   """
   recibe 2 posiciones en forma de tupla y calcula su diferencia y la suma ayudando a a-star a estimar
   la distancia entre el objeto y el vehiculo que está yendo a buscarlo.
   La distancia es cuántas cuadras tendrías que caminar horizontal y verticalmente para ir de un punto a otro
   sin cortar esquinas.
   """
   ax, ay = a #desglozamos las tuplas
   bx , by = b
   return abs(ax - bx) + abs(ay - by)

def costo_extra(tablero, pos):
    """
    en caso de que el camino más corto sea pasando por una zona de mina o pasando dentro de su radio
    (cosa que causaría la colisión) se le agrega un peso extra al camino para que el vehículo decida 
    no ir por ahí
    """
    x, y = pos
    if tablero.colision_minas(x, y):
        return 20 #este es el costo extra que se le agrega  
    return 0

def a_star(vehiculo, tablero, pos_obj):
    """
    Algoritmo para calcular el camino más corto desde un nodo de un grafo hacia un objetivo establecido
    es más eficiente que un BFS/Dijkstra porque no explora todos los nodos sino que explora los necesarios
    para encontrar el camino más corto.
    
    entrada: el vehiculo que se va a mover, el tablero y la posición final del recurso
    salida: devuelve el camino que debe recorrer el vehículo para llegar al recurso de la forma más rápida posible
    """
    #guardamos la frontera de nuestro nodo de inicio (posicion del vehiculo en una cola con prioridad)
    frontera = PriorityQueue()
    frontera.put((0, vehiculo.posicion))  # prioridad, nodo
    
    viene_de = dict()
    costo_distancia = dict() #diccionarios para almacenar de donde viene el nodo (armar el camino) y el costo que tiene ese recorrido
    viene_de[vehiculo.posicion] = None
    costo_distancia[vehiculo.posicion] = 0

    while not frontera.empty():
        _, current = frontera.get() #frontera.get nos devuelve una tupla con la prioridad y la posicion que es lo que nos interesa
        
        if current == pos_obj:
            break
            #si encontramos el objetivo rompemos el bucle para una mayor eficiencia
            
        for siguiente in get_vecinos(tablero, current): #para cada nodo el la lista de vecinos hacemos lo siguiente
            nuevo_costo = costo_distancia[current] + 1 + costo_extra(tablero, siguiente) #calculamos el nuevo costo
            if siguiente not in costo_distancia or nuevo_costo < costo_distancia[siguiente]:
                #si no lo habíamos explorado antes o llegamos desde un nodo cuyo costo es más barato:
                costo_distancia[siguiente] = nuevo_costo #le asignamos su costo (nuevo o reasignado)
                prioridad = nuevo_costo + heuristica(pos_obj, siguiente) #le establecemos la prioridad para insertarlo en la cola de las fronteras 
                frontera.put((prioridad, siguiente)) #lo añadimos en los nodos próximos a explorar
                viene_de[siguiente] = current #indicamos de donde viene

    # Reconstruimos el camino
    camino = []
    node = pos_obj
    while node is not None:
        camino.append(node)
        node = viene_de.get(node)
    camino.reverse()
    return camino

def dijkstra_recurso_mas_cercano(vehiculo, tablero):

    """
    Algoritmo de Dijkstra para encontrar el recurso más cercano desde la posición del vehículo.
    
    Entrada:
        - vehiculo: objeto Vehiculo
        - tablero: objeto Tablero
    
    Salida:
        - La posición (x, y) del recurso más cercano disponible.
    """
    
    frontera = PriorityQueue()
    frontera.put((0, vehiculo.posicion))  # prioridad, nodo inicial
    
    costo_distancia = dict()  # costo acumulado para cada nodo
    costo_distancia[vehiculo.posicion] = 0
    
    while not frontera.empty():
        _, current = frontera.get()
        
        if current in tablero.pos_recursos:
            recurso = tablero.pos_recursos[current]
            if recurso.estado == "disponible" and recurso.categoria in vehiculo.tipo_carga_permitida and recurso.asignado_a == None:
                recurso.asignado_a = vehiculo
                return current
        
        for siguiente in get_vecinos(tablero, current):
            nuevo_costo = costo_distancia[current] + 1 + costo_extra(tablero, siguiente)
            
            if siguiente not in costo_distancia or nuevo_costo < costo_distancia[siguiente]:
                costo_distancia[siguiente] = nuevo_costo
                frontera.put((nuevo_costo, siguiente))
    
    # Si no se encuentra ningún recurso disponible
    return None