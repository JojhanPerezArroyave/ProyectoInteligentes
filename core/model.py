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
        # Diccionario para registrar los números en el mapa
        self.visited_numbers = {}
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

    def place_agent_number(self, pos, number):
        # Registrar el número de la casilla en self.visited_numbers
        self.visited_numbers[pos] = number
        # Asegurar que el número se queda en la celda aunque Bomberman no esté
        self.grid.place_agent(NumberMarker(pos, self, number), pos)

    def step(self):
        # Avanzar en el tiempo
        self.schedule.step()

class NumberMarker(Agent):
    def __init__(self, pos, model, number):
        super().__init__(pos, model)
        self.number = number

    def step(self):
        pass  # Los números no hacen nada, son solo decorativos
        
