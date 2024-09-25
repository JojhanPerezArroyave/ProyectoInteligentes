from collections import deque

def breadth_first_search(start, goal, model):
    queue = deque([start])
    visited = {start}
    came_from = {start: None}

    while queue:
        current = queue.popleft()
        
        if current == goal:
            return reconstruct_path(came_from, current)
        
        neighbors = model.grid.get_neighborhood(current, moore=False, include_center=False)
        for neighbor in neighbors:
            if neighbor not in visited and model.grid.is_cell_empty(neighbor):
                visited.add(neighbor)
                queue.append(neighbor)
                came_from[neighbor] = current
                
    return None  # No se encontró la meta

def reconstruct_path(came_from, current):
    path = []
    while current:
        path.append(current)
        current = came_from[current]
    path.reverse()
    return path
