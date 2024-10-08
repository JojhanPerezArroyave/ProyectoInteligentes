from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from agents.bomberman import Bomberman
from agents.numberMarker import NumberMarker
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
        self.visited_numbers = {}
        self.algorithm = algorithm  
        self.load_map(map_file)

    def get_map_dimensions(self, map_file):
        with open(map_file, "r") as f:
            lines = f.readlines()
            height = len(lines)
            width = len(lines[0].strip().split(','))
        return width, height

    def load_map(self, map_file):
        with open(map_file, "r") as f:
            lines = f.readlines()
            bomberman_position = None 
            valid_positions = []  

            for y, line in enumerate(reversed(lines)): 
                elements = line.strip().split(',')
                for x, elem in enumerate(elements):
                    if elem == "C_b":  
                        bomberman_position = (x, y)
                    elif elem == "C":
                        valid_positions.append((x, y))
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

            if not bomberman_position:
                if valid_positions:
                    bomberman_position = random.choice(valid_positions)
                else:
                    raise ValueError("No hay posiciones válidas en el mapa para colocar a Bomberman.")

            bomberman = Bomberman(bomberman_position, self)
            self.grid.place_agent(bomberman, bomberman_position)
            self.schedule.add(bomberman)


    def place_agent_number(self, pos, number):
        """
            Marca una casilla en el mapa con un número que representa el orden en que fue visitada.

            Args:
                pos (tuple): La posición en la grilla.
                number (int): El número que representa el orden de la visita.
        """
        self.visited_numbers[pos] = number
        self.grid.place_agent(NumberMarker(pos, self, number), pos)

    def step(self):
        self.schedule.step()

    def run_search_algorithm(self, start, goal):
        """
            Ejecuta el algoritmo de búsqueda seleccionado por el usuario.

            Args:
                start (tuple): La posición inicial de Bomberman.
                goal (tuple): La posición objetivo (normalmente la salida bajo la roca).

            Returns:
                list: El camino encontrado hacia la salida.
        """
        if self.algorithm == "BFS":
            return breadth_first_search(start, goal, self)
        elif self.algorithm == "DFS":
            return depth_first_search(start, goal, self)
        elif self.algorithm == "UCS":
            return uniform_cost_search(start, goal, self)
    

        
