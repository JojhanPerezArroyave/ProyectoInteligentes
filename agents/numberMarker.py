from mesa import Agent
class NumberMarker(Agent):
    def __init__(self, pos, model, number):
        super().__init__(pos, model)
        self.number = number

    def step(self):
        pass 