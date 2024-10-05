from mesa import Agent
from agents.rock import Rock

class Bomberman(Agent):
    def __init__(self, pos, model):
        super().__init__(pos, model)
        self.pos = pos
        self.path = []  # Aquí guardaremos el camino hacia la salida
    
    def move(self):
        # Encontrar la posición de la salida
        exit_position = self.find_exit_position()
        
        # Verificar si se ha encontrado la salida
        if exit_position is not None:
            # Si no hay un camino calculado o ya llegamos al final, calculamos un nuevo camino
            if not self.path:
                self.path = self.model.run_search_algorithm(self.pos, exit_position)
                print(f"Camino encontrado: {self.path}")
            
            # Mover a Bomberman a la siguiente posición del camino si existe un camino
            if self.path:
                next_position = self.path.pop(0)
                self.model.grid.move_agent(self, next_position)
            
            # Imprimir información en consola
            print(f"Posición actual de Bomberman: {self.pos}")
            print(f"Posición de la salida: {exit_position}")
            possible_steps = self.model.grid.get_neighborhood(self.pos, moore=False, include_center=False)
            valid_steps = [pos for pos in possible_steps if self.model.grid.is_cell_empty(pos)]
            print(f"Casillas válidas para moverse: {valid_steps}")
        else:
            print("No se ha encontrado la salida.")
    
    def find_exit_position(self):
        # Encontrar la roca con la salida
        for agent in self.model.schedule.agents:
            if isinstance(agent, Rock) and agent.has_exit:
                return agent.pos
        return None  # Debería siempre encontrar una roca con salida

    def step(self):
        self.move()
