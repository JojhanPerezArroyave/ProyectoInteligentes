from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from agents.bomberman import Bomberman
from agents.rock import Rock
from agents.metal import Metal
from utils.search_algorithms import breadth_first_search, depth_first_search, uniform_cost_search
import random

class BombermanModel(Model):
    def __init__(self,  map_file, algorithm):
        super().__init__()
        self.grid_width, self.grid_height = self.get_map_dimensions(map_file)
        self.grid = MultiGrid(self.grid_width, self.grid_height, torus=False)
        self.schedule = RandomActivation(self)
        # Diccionario para registrar los números en el mapa
        self.visited_numbers = {}

        self.algorithm = algorithm  # Guardar el algoritmo seleccionado
        # Cargar el mapa desde un archivo de texto
        self.load_map(map_file)

    def get_map_dimensions(self, map_file):
        """Calcula las dimensiones del mapa basándose en el archivo de texto."""
        with open(map_file, "r") as f:
            lines = f.readlines()
            height = len(lines)
            width = len(lines[0].strip().split(','))
        return width, height

    def load_map(self, map_file):
        with open(map_file, "r") as f:
            lines = f.readlines()
            for y, line in enumerate(reversed(lines)):  # Invertir el orden de las filas
                elements = line.strip().split(',')
                for x, elem in enumerate(elements):
                    if elem == "C":
                        continue  # Casilla de camino, no necesita agente
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

    def run_search_algorithm(self, start, goal):
        """Ejecuta el algoritmo de búsqueda basado en la selección del usuario."""
        if self.algorithm == "BFS":
            return breadth_first_search(start, goal, self)
        elif self.algorithm == "DFS":
            return depth_first_search(start, goal, self)
        elif self.algorithm == "UCS":
            return uniform_cost_search(start, goal, self)
    

class NumberMarker(Agent):
    def __init__(self, pos, model, number):
        super().__init__(pos, model)
        self.number = number

    def step(self):
        pass  # Los números no hacen nada, son solo decorativos
        
