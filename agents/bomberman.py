from mesa import Agent
from collections import deque
from agents.bomb import Bomb
from agents.fire import Fire
from agents.rock import Rock
from agents.metal import Metal
from agents.numberMarker import NumberMarker
from agents.joker import Joker
from utils.search_algorithms import breadth_first_search_without_markers, get_neighbors_in_orthogonal_order


class Bomberman(Agent):
    def __init__(self, pos, model):
        super().__init__(pos, model)
        self.pos = pos
        self.path = []  # Camino hacia la salida
        self.safe_path = []  # Camino hacia una posición segura
        self.return_path = []  # Camino de regreso al camino original
        self.power = 1  # Poder de destrucción inicial de la bomba
        self.exit_found = False  # Bandera para rastrear si Bomberman encontró la salida
        self.placed_bomb = False  # Rastrea si ya se ha colocado una bomba
        self.waiting_for_explosion = False  # Indica si Bomberman está esperando que la bomba y el fuego desaparezcan
        self.safe_position = None  # Posición segura donde Bomberman esperará
        self.exit_position =  self.find_exit_position()  # Posición de la roca con la salida

    def move(self):
        """Controla los movimientos de Bomberman y gestiona la lógica de colocación de bombas y movimiento seguro."""
        # Si está esperando en la posición segura, verifica si la explosión ha terminado
        if self.waiting_for_explosion:
            if self.is_explosion_over():
            
                self.waiting_for_explosion = False
                self.placed_bomb = False
                self.calculate_return_path()  # Calcula el camino de regreso al camino original
            else:
                self.follow_safe_path()  # Moverse en el camino seguro paso a paso
            return

        # Si Bomberman está en el proceso de regresar al camino original
        if self.return_path:
            self.follow_return_path()  # Seguir el camino de regreso paso por paso
            return

        # Verifica si Bomberman encuentra una roca con un ítem de poder
        rock = self.model.grid.get_cell_list_contents([self.pos])
        for obj in rock:
          
            if isinstance(obj, Joker):
                self.increase_power()  # Incrementa el poder de la bomba
                
                x, y = obj.pos
                number_marker = NumberMarker((x, y), obj.model, obj.value)
                self.model.grid.remove_agent(obj)  # Eliminar la roca
                self.model.grid.place_agent(number_marker, (x, y))  # Colocar el NumberMarker
                self.model.schedule.add(number_marker)  # Añadir al schedule


        exit_position = self.find_exit_position()

        # Si la salida está libre, moverse directamente hacia allí
        if self.exit_found and exit_position and not self.is_block_present(exit_position):
            self.model.grid.move_agent(self, exit_position)
        
            self.model.finish_game()
            return

        # Colocar una bomba si Bomberman está adyacente a la roca con la salida
        if exit_position and self.is_adjacent(exit_position) and not self.exit_found:
            self.place_bomb()
            self.exit_found = True
            self.calculate_safe_path()
            return

        # Calcular un nuevo camino si es necesario
        if exit_position and not self.path:
            self.path = self.model.run_search_algorithm(self.pos, exit_position)
          
        # Colocar bomba si un bloque está en el camino
        if self.is_block_in_the_way() and not self.placed_bomb:
            self.place_bomb()
            self.calculate_safe_path()
        else:
            self.follow_path()  # Moverse si no hay bloque en el camino

    def increase_power(self):
        """Incrementa el poder de destrucción cuando Bomberman encuentra un comodín."""
        self.power += 1
       

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
      

    def calculate_safe_path(self):
        """Calcula el camino paso a paso hacia una posición segura usando un BFS sin marcar casillas."""
        queue = deque([(self.pos, 0)])
        visited = set([self.pos])

        while queue:
            current_pos, _ = queue.popleft()
            if self.is_safe_position(current_pos):
                self.safe_position = current_pos
                self.safe_path = breadth_first_search_without_markers(self.pos, current_pos, self.model)
              
                self.waiting_for_explosion = True
                return

            # Expande vecinos ortogonales
            for neighbor in get_neighbors_in_orthogonal_order(current_pos, self.model):
                if neighbor not in visited and self.is_valid_move_for_escape(neighbor):
                    visited.add(neighbor)
                    queue.append((neighbor, 1))

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
                return False
        return True

    def calculate_return_path(self):
        """Calcula el camino de regreso al último punto explorado antes de ir a la posición segura."""
        if self.path:
            self.return_path = breadth_first_search_without_markers(self.pos, self.path[0], self.model)
            if self.return_path:
                self.return_path = self.return_path[1:]  # Evitar incluir la posición actual en el retorno
          

    def is_explosion_over(self):
        """Verifica si todos los agentes bomba y fuego han sido eliminados del modelo."""
        for agent in self.model.schedule.agents:
            if isinstance(agent, Bomb) or isinstance(agent, Fire):
                return False
        return True

    def follow_safe_path(self):
        """Mueve a Bomberman paso a paso hacia la posición segura."""
        if self.safe_path:
            next_safe_step = self.safe_path.pop(0)
            self.model.grid.move_agent(self, next_safe_step)
          

    def follow_return_path(self):
        """Mueve a Bomberman paso a paso de regreso al camino original."""
        if self.return_path:
            next_return_step = self.return_path.pop(0)
            self.model.grid.move_agent(self, next_return_step)
          

    def find_exit_position(self):
        """Busca la posición de la roca que contiene la salida (R_s)."""
        for agent in self.model.schedule.agents:
            if isinstance(agent, Rock) and agent.has_exit:
                return agent.pos
        return None

    def follow_path(self):
        """Sigue el camino calculado hacia la salida o la siguiente posición."""
        if self.path:
            next_position = self.path.pop(0)
            self.model.grid.move_agent(self, next_position)
        
            if next_position == self.exit_position:  
                self.model.finish_game()



    def step(self):
        self.model.update_previous_position(self, self.pos)
        self.move()
        
