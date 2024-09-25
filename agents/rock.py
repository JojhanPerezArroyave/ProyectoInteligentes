from mesa import Agent

class Rock(Agent):
    def __init__(self, pos, model):
        super().__init__(pos, model)
        self.pos = pos

    def step(self):
        # Las rocas no tienen acciones en este entregable
        pass
