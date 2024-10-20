from mesa import Agent
from agents.rock import Rock
class Bomberman(Agent):
    def __init__(self, pos, model):
        super().__init__(pos, model)
        self.pos = pos
        self.path = [] 
    
    def move(self):
        """
            Calcula y sigue el camino hacia la salida en cada paso del modelo.
            Si no hay un camino precalculado, se utiliza el algoritmo de búsqueda seleccionado
            para encontrarlo.
        """
        exit_position = self.find_exit_position()
        
        if exit_position is not None:
            # Si no hay un camino calculado o ya llegamos al final, calculamos un nuevo camino
            if not self.path:
                self.path = self.model.run_search_algorithm(self.pos, exit_position)
                print(f"Camino encontrado: {self.path}")
            
            # Si exite un camino, movemos al agente a la siguiente posición
            if self.path:
                next_position = self.path.pop(0)
                self.model.update_previous_position(self, self.pos)
                self.model.grid.move_agent(self, next_position)
            
            print(f"Posición de la salida: {exit_position}")
            possible_steps = self.model.grid.get_neighborhood(self.pos, moore=False, include_center=False)
            valid_steps = [pos for pos in possible_steps if self.model.grid.is_cell_empty(pos)]
            print(f"Casillas válidas para moverse: {valid_steps}")

        else:
            print("No se ha encontrado la salida.")
    
    def find_exit_position(self):
        """
            Busca la posición de la roca que contiene la salida (R_s).

            Returns:
                tuple: La posición de la roca con la salida, si existe. Si no, devuelve None.
        """
        for agent in self.model.schedule.agents:
            if isinstance(agent, Rock) and agent.has_exit:
                return agent.pos
        return None  

    def step(self):
        self.move()
