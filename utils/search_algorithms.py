from collections import deque

def breadth_first_search(start, goal, model):
    queue = deque([start])
    visited = {start}
    came_from = {start: None}
    
    # Contador para las casillas analizadas
    step_counter = 0

    while queue:
        current = queue.popleft()

        # Mostrar en el mapa el orden de la casilla analizada
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

    return None  # No se encontró la meta

def depth_first_search(start, goal, model):
    stack = [start]
    visited = {start}
    came_from = {start: None}
    
    # Contador para las casillas analizadas
    step_counter = 0

    while stack:
        current = stack.pop()

        # Mostrar en el mapa el orden de la casilla analizada
        model.place_agent_number(current, step_counter)
        print(f"Casilla {current} marcada con el número {step_counter}")  # Imprimir en consola
        
        step_counter += 1

        # Si estamos en una casilla adyacente a la roca con la salida, terminamos la búsqueda
        if is_adjacent(current, goal):
            return reconstruct_path(came_from, current)
        
        # Obtener vecinos en el orden ortogonal: arriba, derecha, abajo, izquierda
        neighbors = get_neighbors_in_orthogonal_order(current, model)
        for neighbor in neighbors:
            if neighbor not in visited and model.grid.is_cell_empty(neighbor):
                visited.add(neighbor)
                stack.append(neighbor)
                came_from[neighbor] = current

    return None  # No se encontró la meta


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
        (x, y + 1),  # Arriba
        (x + 1, y),  # Derecha
        (x, y - 1),  # Abajo
        (x - 1, y)   # Izquierda
    ]
    # Filtrar los vecinos válidos que están dentro de los límites del mapa y son caminos
    valid_neighbors = [n for n in neighbors if model.grid.out_of_bounds(n) == False]
    return valid_neighbors

