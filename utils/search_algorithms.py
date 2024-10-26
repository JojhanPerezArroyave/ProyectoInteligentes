from collections import deque
from heapq import heappush, heappop
from itertools import count

from agents.metal import Metal
from agents.rock import Rock


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
            if neighbor not in visited and is_valid_move(neighbor, model):
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
            if neighbor not in visited and is_valid_move(neighbor, model):
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
            if neighbor not in visited and is_valid_move(neighbor, model):
                new_cost = current_cost + 1  # Asumimos que el costo de moverse es 1
                heappush(queue, (new_cost, next(counter), neighbor))  # Insertar con contador
                came_from[neighbor] = current_node

    return None  # Si no se encuentra un camino

def beam_search(start, goal, model, heuristic ,beam_width=2):
    """
    Implementación del algoritmo Beam Search.
    
    Args:
        start (tuple): Posición inicial de Bomberman.
        goal (tuple): Posición objetivo (normalmente la salida bajo una roca).
        model (BombermanModel): El modelo de Mesa que contiene el mapa y los agentes.
        beam_width (int): El número máximo de nodos a expandir por nivel.
    
    Returns:
        list: El camino encontrado desde el inicio hasta la meta.
    """
    queue = [(start, 0)]  # (nodo actual, valor heurístico)
    came_from = {start: None}
    step_counter = 0

    while queue:
        # Ordenar la lista según el valor heurístico (distancia a la meta)
        queue.sort(key=lambda x: x[1])
        
        # Limitar la cantidad de nodos a expandir por el ancho del haz (beam_width)
        queue = queue[:beam_width]
        
        # Lista temporal para almacenar los nuevos nodos a expandir
        next_queue = []
        
        for current_node, _ in queue:
            model.place_agent_number(current_node, step_counter)
            print(f"Casilla {current_node} marcada con el número {step_counter}")  # Imprimir en consola
            step_counter += 1

            # Si estamos en una casilla adyacente a la roca con la salida, terminamos la búsqueda
            if is_adjacent(current_node, goal):
                return reconstruct_path(came_from, current_node)
            
            # Obtener vecinos en el orden ortogonal
            neighbors = get_neighbors_in_orthogonal_order(current_node, model)

            for neighbor in neighbors:
                if neighbor not in came_from and is_valid_move(neighbor, model):
                    # Calcular heurística: distancia de Manhattan a la meta
                    heuristic_value = heuristic(neighbor, goal)
                    came_from[neighbor] = current_node
                    next_queue.append((neighbor, heuristic_value))
        
        # Actualizar la cola con los nuevos nodos a expandir
        queue = next_queue

    return None  # Si no se encuentra un camino

def hill_climbing(start, goal, model, heuristic):
    """
    Implementación del algoritmo de búsqueda Hill Climbing.
    
    Args:
        start (tuple): Posición inicial de Bomberman.
        goal (tuple): Posición objetivo (normalmente la salida bajo una roca).
        model (BombermanModel): El modelo de Mesa que contiene el mapa y los agentes.
        heuristic (function): Función heurística para calcular la distancia a la meta.
    
    Returns:
        list: El camino encontrado desde el inicio hasta la meta.
    """
    current_node = start
    came_from = {start: None}
    step_counter = 0

    while current_node != goal:
        model.place_agent_number(current_node, step_counter)
        print(f"Casilla {current_node} marcada con el número {step_counter}")  # Imprimir en consola
        step_counter += 1

        # Obtener vecinos en el orden ortogonal
        neighbors = get_neighbors_in_orthogonal_order(current_node, model)
        # Filtrar vecinos válidos y calcular sus valores heurísticos
        valid_neighbors = [
            (neighbor, heuristic(neighbor, goal))
            for neighbor in neighbors
            if is_valid_move(neighbor, model) and neighbor not in came_from
        ]

        # Si no hay vecinos válidos, alcanzamos un óptimo local
        if not valid_neighbors:
            print("Óptimo local alcanzado, no hay mejoras posibles.")
            return reconstruct_path(came_from, current_node)
        
        # Elegir el vecino con el menor valor heurístico
        next_node, _ = min(valid_neighbors, key=lambda x: x[1])

        # Si el vecino seleccionado no mejora, terminamos (óptimo local)
        if heuristic(next_node, goal) >= heuristic(current_node, goal):
            print("Óptimo local alcanzado, no se puede avanzar.")
            return reconstruct_path(came_from, current_node)

        # Actualizar el camino
        came_from[next_node] = current_node
        current_node = next_node

    # Reconstruir el camino hacia la salida
    return reconstruct_path(came_from, current_node)

def a_star_search(start, goal, model, heuristic):
    """
    Implementación del algoritmo de búsqueda A* (A estrella).
    
    Args:
        start (tuple): Posición inicial de Bomberman.
        goal (tuple): Posición objetivo (normalmente la salida bajo una roca).
        model (BombermanModel): El modelo de Mesa que contiene el mapa y los agentes.
        heuristic (function): Función heurística para estimar la distancia a la meta.
    
    Returns:
        list: El camino encontrado desde el inicio hasta la meta.
    """
    # Inicializar la cola de prioridad con un contador para desempate
    queue = []
    counter = count()  # Generador de contadores para desempatar
    heappush(queue, (0, next(counter), start))  # (f(n), contador, nodo)
    
    came_from = {start: None}
    g_cost = {start: 0}  # Diccionario para almacenar el costo g(n) de cada nodo
    step_counter = 0

    while queue:
        # Extraer el nodo con el menor valor de f(n) y menor contador
        _, _, current_node = heappop(queue)
        
        # Marcar la casilla actual con el número de visita
        model.place_agent_number(current_node, step_counter)
        print(f"Casilla {current_node} marcada con el número {step_counter}")  # Imprimir en consola
        step_counter += 1

        # Si el nodo actual está adyacente a la meta, se reconstruye el camino
        if is_adjacent(current_node, goal):
            return reconstruct_path(came_from, current_node)
        
        # Obtener vecinos en el orden ortogonal
        neighbors = get_neighbors_in_orthogonal_order(current_node, model)

        for neighbor in neighbors:
            if is_valid_move(neighbor, model):
                # Calcular g(n) para el vecino
                tentative_g_cost = g_cost[current_node] + 1  # Se asume un costo de 1 por movimiento
                
                # Si encontramos un camino más corto a neighbor, o es la primera vez que lo encontramos
                if neighbor not in g_cost or tentative_g_cost < g_cost[neighbor]:
                    g_cost[neighbor] = tentative_g_cost
                    f_cost = tentative_g_cost + heuristic(neighbor, goal)  # f(n) = g(n) + h(n)
                    heappush(queue, (f_cost, next(counter), neighbor))
                    came_from[neighbor] = current_node

    return None  # Si no se encuentra un camino


def is_adjacent(pos1, pos2):
    """Verifica si dos posiciones están una al lado de la otra."""
    x1, y1 = pos1
    x2, y2 = pos2
    return abs(x1 - x2) + abs(y1 - y2) == 1

def manhattan_distance(pos1, pos2):
    """
    Calcula la distancia de Manhattan entre dos posiciones.
    """
    x1, y1 = pos1
    x2, y2 = pos2
    return abs(x1 - x2) + abs(y1 - y2)

import math

def euclidean_distance(pos1, pos2):
    '''
    Calcula la distancia euclidiana entre dos posiciones.
    '''
    x1, y1 = pos1
    x2, y2 = pos2
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


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

def is_valid_move(pos, model):
    cell_contents = model.grid.get_cell_list_contents(pos)
    for obj in cell_contents:
        if isinstance(obj, Metal):
            return False 
    
    return True  

