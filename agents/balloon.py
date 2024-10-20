from mesa import Agent
import random

class Balloon(Agent):
    def __init__(self, post, model) :
        super().__init__(post, model)
        self.post = post

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(self.pos, moore=False, include_center=False)
        valid_steps = [pos for pos in possible_steps if self.model.grid.is_cell_empty(pos)]       

        if valid_steps:
            new_position = random.choice(valid_steps)
            self.model.grid.move_agent(self, new_position)

    def step(self):
        self.move()