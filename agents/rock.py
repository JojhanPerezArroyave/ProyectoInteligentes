from mesa import Agent

class Rock(Agent):
    def __init__(self, pos, model, has_exit=False):
        super().__init__(pos, model)
        self.pos = pos
        self.has_exit = has_exit

    def step(self):
        # Las rocas no tienen acciones en este entregable
        pass
