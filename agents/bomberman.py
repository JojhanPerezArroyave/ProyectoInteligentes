from mesa import Agent
from agents.rock import Rock

class Bomberman(Agent):
    def __init__(self, pos, model):
        super().__init__(pos, model)
        self.pos = pos
        self.path = [] 
        self.power = 1  # Poder de destrucción inicial de la bomba
        self.exit_found = False  # Bandera para rastrear si Bomberman encontró la salida

    def move(self):
        """
        Calcula y sigue el camino hacia la salida en cada paso del modelo.
        Coloca una bomba si Bomberman encuentra un obstáculo en su camino.
        """
        exit_position = self.find_exit_position()
        
        # Si la salida está libre, moverse directamente hacia allí
        if self.exit_found and exit_position and not self.is_block_present(exit_position):
            self.model.grid.move_agent(self, exit_position)
            print("¡Bomberman ha alcanzado la salida!")
            self.model.finish_game()
            return

        # Colocar una bomba si Bomberman está adyacente a la roca con la salida
        if exit_position and self.is_adjacent(exit_position) and not self.exit_found:
            self.place_bomb()  # Coloca una bomba para destruir la roca de salida
            self.exit_found = True  # Marca que encontró la salida y colocó la bomba
            self.move_to_safe_position()
            return

        # Calcular un nuevo camino si es necesario
        if exit_position and not self.path:
            self.path = self.model.run_search_algorithm(self.pos, exit_position)
            print(f"Camino encontrado: {self.path}")

        # Colocar bomba si un bloque está en el camino
        if self.is_block_in_the_way():
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
        print(f"Bomba colocada con tiempo de detonación: {self.power + 2}")

    def move_to_safe_position(self):
        """Busca una posición segura fuera del rango de la explosión y se mueve hacia ella."""
        safe_positions = [
            pos for pos in self.model.grid.get_neighborhood(self.pos, moore=False, include_center=False)
            if self.is_safe_position(pos)
        ]
        if safe_positions:
            safe_pos = safe_positions[0]
            self.model.grid.move_agent(self, safe_pos)
            print(f"Bomberman se movió a una posición segura: {safe_pos}")
        else:
            print("No hay posiciones seguras alrededor; Bomberman puede quedar en peligro.")

    def is_safe_position(self, pos):
        """Determina si una posición está fuera del alcance de la explosión."""
        x, y = self.pos
        px, py = pos
        return abs(px - x) > self.power or abs(py - y) > self.power

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
