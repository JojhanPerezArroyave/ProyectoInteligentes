from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import Choice
from core.model import BombermanModel, NumberMarker
from agents.bomberman import Bomberman
from agents.rock import Rock
from agents.metal import Metal

def agent_portrayal(agent):
    portrayal = {"Shape": "rect", "Filled": "true", "Layer": 0}

    if isinstance(agent, NumberMarker):
        portrayal["Shape"] = "rect"
        portrayal["Color"] = "white"
        portrayal["w"] = 1
        portrayal["h"] = 1
        portrayal["text"] = str(agent.number)
        portrayal["text_color"] = "black"
        return portrayal  # No necesitamos seguir evaluando otros agentes aquí

    if hasattr(agent, 'model') and agent.pos in agent.model.visited_numbers:
        portrayal["text"] = str(agent.model.visited_numbers[agent.pos])
        portrayal["text_color"] = "red"
    
    if isinstance(agent, Bomberman):
        portrayal["Shape"] = "circle"
        portrayal["Color"] = "blue"
        portrayal["r"] = 0.8
    
    elif isinstance(agent, Rock):
        portrayal["Color"] = "brown"
        portrayal["w"] = 1
        portrayal["h"] = 1
        if agent.has_exit:
            portrayal["text"] = "SALIDA"
            portrayal["text_color"] = "white"
    
    elif isinstance(agent, Metal):
        portrayal["Color"] = "gray"
        portrayal["w"] = 1
        portrayal["h"] = 1
    
    return portrayal

map_file = "data/map.txt"
model = BombermanModel(map_file, "BFS")

grid = CanvasGrid(agent_portrayal, model.grid_width, model.grid_height, 500, 500)

# Selección de algoritmo
algorithm_choice = Choice("Algoritmo de búsqueda", value="BFS", choices=["BFS", "DFS", "UCS"])

server = ModularServer(
    BombermanModel, [grid], "Bomberman Model", {"map_file": map_file, "algorithm": algorithm_choice}
)
server.port = 8521
server.launch()
