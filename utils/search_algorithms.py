from collections import deque
from heapq import heappush, heappop
from itertools import count


def breadth_first_search(start, goal, model):
    queue = deque([start])
    visited = {start}
    came_from = {start: None}
    step_counter = 0

    while queue:
        current = queue.popleft()
        model.place_agent_number(current, step_counter)
        print(f"Casilla {current} marcada con el número {step_counter}")  # Imprimir en consola
        step_counter += 1

        # Si estamos en una casilla adyacente a la roca con la salida, terminamos la búsqueda
        if is_adjacent(current, goal):
            return reconstruct_path(came_from, current)
        
        # Obtener vecinos en el orden ortogonal
        neighbors = get_neighbors_in_orthogonal_order(current, model)

        for neighbor in neighbors:
            if neighbor not in visited and model.grid.is_cell_empty(neighbor):
                visited.add(neighbor)
                queue.append(neighbor)
                came_from[neighbor] = current

    return None 

def depth_first_search(start, goal, model):
    stack = [start]
    visited = {start}
    came_from = {start: None}
    step_counter = 0

    while stack:
        current = stack.pop()
        model.place_agent_number(current, step_counter)
        print(f"Casilla {current} marcada con el número {step_counter}")  
        step_counter += 1

        # Si estamos en una casilla adyacente a la roca con la salida, terminamos la búsqueda
        if is_adjacent(current, goal):
            return reconstruct_path(came_from, current)
        
        # Obtener vecinos en el orden ortogonal
        neighbors = get_neighbors_in_orthogonal_order(current, model)

        # Iterar sobre los vecinos en orden inverso para que el orden sea arriba, derecha, abajo, izquierda, 
        # porque en una pila se toma la última casilla que se agregó
        for neighbor in reversed(neighbors):
            if neighbor not in visited and model.grid.is_cell_empty(neighbor):
                visited.add(neighbor)
                stack.append(neighbor)
                came_from[neighbor] = current

    return None 

def uniform_cost_search(start, goal, model):
    """
    Implementación del algoritmo de búsqueda por costo uniforme (UCS).
    
    Args:
        start (tuple): Posición inicial de Bomberman.
        goal (tuple): Posición objetivo (normalmente la salida bajo una roca).
        model (BombermanModel): El modelo de Mesa que contiene el mapa y los agentes.
    
    Returns:
        list: El camino encontrado desde el inicio hasta la meta.
    """
    # Inicializar la cola de prioridad con un contador para desempate
    queue = []
    counter = count()  # Generador de contadores
    heappush(queue, (0, next(counter), start))  # (costo acumulado, contador, nodo)
    
    visited = set()
    came_from = {start: None}
    step_counter = 0

    while queue:
        # Extraer el nodo con el menor costo acumulado y menor contador
        current_cost, _, current_node = heappop(queue)
        
        # Si el nodo actual ya ha sido visitado, saltarlo
        if current_node in visited:
            continue
        
        # Marcar el nodo como visitado
        visited.add(current_node)
        
        # Marcar la casilla con el número de visita
        model.place_agent_number(current_node, step_counter)
        print(f"Casilla {current_node} marcada con el número {step_counter}")  # Imprimir en consola
        step_counter += 1
        
        # Verificar si el nodo actual está adyacente a la meta
        if is_adjacent(current_node, goal):
            return reconstruct_path(came_from, current_node)
        
        # Obtener vecinos en el orden ortogonal: izquierda, arriba, derecha, abajo
        neighbors = get_neighbors_in_orthogonal_order(current_node, model)
        
        for neighbor in neighbors:
            if neighbor not in visited and model.grid.is_cell_empty(neighbor):
                new_cost = current_cost + 1  # Asumimos que el costo de moverse es 1
                heappush(queue, (new_cost, next(counter), neighbor))  # Insertar con contador
                came_from[neighbor] = current_node

    return None  # Si no se encuentra un camino


def is_adjacent(pos1, pos2):
    """Verifica si dos posiciones están una al lado de la otra."""
    x1, y1 = pos1
    x2, y2 = pos2
    return abs(x1 - x2) + abs(y1 - y2) == 1

def reconstruct_path(came_from, current):
    path = []
    while current:
        path.append(current)
        current = came_from[current]
    path.reverse()
    return path

def get_neighbors_in_orthogonal_order(pos, model):
    x, y = pos
    # Orden ortogonal: arriba, derecha, abajo, izquierda
    neighbors = [
        (x - 1, y),  # Izquierda
        (x, y + 1),  # Arriba
        (x + 1, y),  # Derecha
        (x, y - 1)   # Abajo
    ]
    # Filtrar los vecinos válidos que están dentro de los límites del mapa y son caminos
    valid_neighbors = [n for n in neighbors if model.grid.out_of_bounds(n) == False]
    return valid_neighbors

