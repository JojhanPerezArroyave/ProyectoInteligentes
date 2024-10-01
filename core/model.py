from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from agents.bomberman import Bomberman
from agents.rock import Rock
from agents.metal import Metal
import random

class BombermanModel(Model):
    def __init__(self, width, height, map_file):
        super().__init__()
        self.grid = MultiGrid(width, height, torus=False)
        self.schedule = RandomActivation(self)
        # Cargar el mapa desde un archivo de texto
        self.load_map(map_file)

    def load_map(self, map_file):
        with open(map_file, "r") as f:
            lines = f.readlines()
            # Invertir el orden de las filas
            for y, line in enumerate(reversed(lines)):
                elements = line.strip().split(',')
                for x, elem in enumerate(elements):
                    if elem == "C":
                        # Casilla de camino, no necesita agente
                        continue
                    elif elem == "R":
                        rock = Rock((x, y), self)
                        self.grid.place_agent(rock, (x, y))
                        self.schedule.add(rock)
                    elif elem == "R_s":
                        rock = Rock((x, y), self, has_exit=True)
                        self.grid.place_agent(rock, (x, y))
                        self.schedule.add(rock)
                    elif elem == "M":
                        metal = Metal((x, y), self)
                        self.grid.place_agent(metal, (x, y))
        
        # Posicionar a Bomberman en la esquina superior izquierda del mapa cargado
        bomberman = Bomberman((0, len(lines) - 1), self)
        self.grid.place_agent(bomberman, (0, len(lines) - 1))
        self.schedule.add(bomberman)

    def step(self):
        # Avanzar en el tiempo
        self.schedule.step()
