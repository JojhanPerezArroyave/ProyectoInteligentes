from collections import deque

def breadth_first_search(start, goal, model):
    queue = deque([start])
    visited = {start}
    came_from = {start: None}

    while queue:
        current = queue.popleft()
        # Si estamos en una casilla adyacente a la roca con la salida, terminamos la búsqueda
        if is_adjacent(current, goal):
            return reconstruct_path(came_from, current)
        # Obtener vecinos y verificar si están vacíos
        neighbors = model.grid.get_neighborhood(current, moore=False, include_center=False)
        for neighbor in neighbors:
            if neighbor not in visited and model.grid.is_cell_empty(neighbor):
                visited.add(neighbor)
                queue.append(neighbor)
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
