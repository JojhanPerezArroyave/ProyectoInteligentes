from mesa import Agent

class Bomberman(Agent):
    def __init__(self, pos, model):
        super().__init__(pos, model)
        self.pos = pos
        self.poder_destruccion = 1  # Poder de destrucción inicial
    
    def move(self):
        # Obtener posiciones vecinas que son caminos
        possible_steps = self.model.grid.get_neighborhood(self.pos, moore=False, include_center=False)
        valid_steps = [pos for pos in possible_steps if self.model.grid.is_cell_empty(pos)]
        
        # Mover a Bomberman a una nueva posición
        if valid_steps:
            new_position = self.random.choice(valid_steps)
            self.model.grid.move_agent(self, new_position)
    
    def step(self):
        self.move()
