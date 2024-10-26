from mesa import Agent
from collections import deque
from agents.bomb import Bomb
from agents.fire import Fire
from agents.rock import Rock
from agents.metal import Metal
from agents.numberMarker import NumberMarker
from utils.search_algorithms import breadth_first_search, get_neighbors_in_orthogonal_order


class Bomberman(Agent):
    def __init__(self, pos, model):
        super().__init__(pos, model)
        self.pos = pos
        self.path = [] 
        self.power = 1  # Poder de destrucción inicial de la bomba
        self.exit_found = False  # Bandera para rastrear si Bomberman encontró la salida
        self.placed_bomb = False  # Rastrea si ya se ha colocado una bomba para evitar colocación múltiple
        self.waiting_for_explosion = False  # Indica si Bomberman está esperando que la bomba y el fuego desaparezcan
        self.safe_position = None  # Posición segura a la que se moverá Bomberman para esperar

    def move(self):
        """
        Calcula y sigue el camino hacia la salida en cada paso del modelo.
        Coloca una bomba si Bomberman encuentra un obstáculo en su camino.
        """
        # Si está esperando en posición segura, verifica si la explosión ha terminado
        if self.waiting_for_explosion:
            if self.is_explosion_over():
                print("La explosión ha terminado, Bomberman retoma su camino.")
                self.waiting_for_explosion = False
                self.safe_position = None
                self.placed_bomb = False  # Permitir que coloque una bomba nuevamente si es necesario
            return

        exit_position = self.find_exit_position()

        # Si la salida está libre, moverse directamente hacia allí
        if self.exit_found and exit_position and not self.is_block_present(exit_position):
            self.model.grid.move_agent(self, exit_position)
            print("¡Bomberman ha alcanzado la salida!")
            self.model.finish_game()
            return

        # Colocar una bomba si Bomberman está adyacente a la roca con la salida
        if exit_position and self.is_adjacent(exit_position) and not self.exit_found:
            self.place_bomb()
            self.exit_found = True
            self.move_to_safe_position()
            return

        # Calcular un nuevo camino si es necesario
        if exit_position and not self.path:
            self.path = self.model.run_search_algorithm(self.pos, exit_position)
            print(f"Camino encontrado: {self.path}")

        # Colocar bomba si un bloque está en el camino
        if self.is_block_in_the_way() and not self.placed_bomb:
            self.place_bomb()
            self.move_to_safe_position()
        else:
            self.follow_path()  # Moverse si no hay bloque en el camino

    def increase_power(self):
        """Incrementa el poder de destrucción cuando Bomberman encuentra un comodín."""
        self.power += 1
        print(f"Poder de destrucción incrementado a: {self.power}")

    def is_adjacent(self, position):
        """Comprueba si Bomberman está en una posición adyacente a la dada."""
        x, y = self.pos
        px, py = position
        return abs(px - x) + abs(py - y) == 1

    def is_block_present(self, position):
        """Verifica si hay un bloque en la posición dada."""
        cell_contents = self.model.grid.get_cell_list_contents(position)
        return any(isinstance(obj, Rock) for obj in cell_contents)

    def is_block_in_the_way(self):
        """Verifica si el siguiente paso está bloqueado por un bloque."""
        if self.path:
            next_pos = self.path[0]
            cell_contents = self.model.grid.get_cell_list_contents(next_pos)
            return any(isinstance(obj, Rock) for obj in cell_contents)
        return False

    def place_bomb(self):
        """Coloca una bomba en la posición actual con un temporizador y poder ajustado."""
        from agents.bomb import Bomb  # Importación dentro del método para evitar ciclos
        bomb = Bomb(self.model.next_id(), self.pos, self.model, self.power)
        self.model.grid.place_agent(bomb, self.pos)
        self.model.schedule.add(bomb)
        self.placed_bomb = True
        print(f"Bomba colocada con tiempo de detonación: {self.power + 2}")

    def move_to_safe_position(self):
        """Busca una posición segura fuera del rango de la explosión y se mueve hacia ella paso a paso."""
        queue = deque([(self.pos, 0)])  # (posición actual, distancia desde la bomba)
        visited = set([self.pos])

        while queue:
            current_pos, steps = queue.popleft()

            if self.is_safe_position(current_pos):
                self.safe_position = current_pos
                path_to_safe = self.calculate_path_to_safe(self.pos, current_pos)
                for step in path_to_safe:
                    self.model.grid.move_agent(self, step)
                    print(f"Bomberman se movió a {step} en búsqueda de una posición segura")
                self.waiting_for_explosion = True  # Esperar a que termine la explosión
                return  # Se detiene en la primera posición segura encontrada

            # Expande vecinos ortogonales
            for neighbor in get_neighbors_in_orthogonal_order(current_pos, self.model):
                if neighbor not in visited and self.is_valid_move_for_escape(neighbor):
                    visited.add(neighbor)
                    queue.append((neighbor, steps + 1))

        print("No hay posiciones seguras alrededor; Bomberman puede quedar en peligro.")

    def is_safe_position(self, pos):
        """Determina si una posición está fuera del alcance de la explosión."""
        x, y = self.pos
        px, py = pos
        return abs(px - x) > self.power or abs(py - y) > self.power

    def is_valid_move_for_escape(self, pos):
        """Determina si Bomberman puede moverse a una posición para escapar de la explosión."""
        cell_contents = self.model.grid.get_cell_list_contents(pos)
        for obj in cell_contents:
            if isinstance(obj, Rock) or isinstance(obj, Metal):
                return False  # Obstáculos sólidos
        return True  # Posiciones libres o `NumberMarker` permitidos

    def calculate_path_to_safe(self, start, goal):
        """Calcula el camino paso a paso hacia una posición segura."""
        path = breadth_first_search(start, goal, self.model)
        if path:
            return path[1:]  # Excluir la posición inicial
        return []

    def is_explosion_over(self):
        """Verifica si todos los agentes bomba y fuego han sido eliminados del modelo."""
        for agent in self.model.schedule.agents:
            if isinstance(agent, Bomb) or isinstance(agent, Fire):
                return False
        return True

    def find_exit_position(self):
        """Busca la posición de la roca que contiene la salida (R_s)."""
        for agent in self.model.schedule.agents:
            if isinstance(agent, Rock) and agent.has_exit:
                return agent.pos
        return None

    def follow_path(self):
        """Sigue el camino calculado."""
        if self.path:
            next_position = self.path.pop(0)
            self.model.grid.move_agent(self, next_position)

    def step(self):
        self.move()
