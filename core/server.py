from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import Choice
from agents.balloon import Balloon
from agents.bomb import Bomb
from agents.fire import Fire
from core.model import BombermanModel, NumberMarker
from agents.bomberman import Bomberman
from agents.rock import Rock
from agents.metal import Metal
from agents.joker import Joker

def agent_portrayal(agent):
    portrayal = {"Shape": "rect", "Filled": "true", "Layer": 0}

    if isinstance(agent, NumberMarker):
        portrayal["Shape"] = "rect"
        portrayal["Color"] = "white"
        portrayal["w"] = 1
        portrayal["h"] = 1
        portrayal["text"] = str(agent.number)
        portrayal["text_color"] = "black"
        return portrayal 

    if hasattr(agent, 'model') and agent.pos in agent.model.visited_numbers:
        portrayal["text"] = str(agent.model.visited_numbers[agent.pos])
        portrayal["text_color"] = "red"
    
    if isinstance(agent, Bomberman):
        portrayal["Shape"] = "assets/Bomberman.jpg"

    elif isinstance(agent, Rock):
        portrayal["Shape"] = "assets/Rocas.jpg"
        if agent.has_exit:
            portrayal["Shape"] = "assets/Roca-Salida.jpg"
    
    elif isinstance(agent, Metal):
        portrayal["Shape"] = "assets/Metal.jpg"

    elif isinstance(agent, Balloon):
        portrayal["Shape"] = "assets/Globo.jpg"

    elif isinstance(agent, Bomb):
        portrayal["Shape"] = "assets/Bomba.jpg"

    elif isinstance(agent, Fire):
        portrayal["Shape"] = "assets/Fuego.jpg"
    
    elif isinstance(agent, Joker):
        portrayal["Shape"] = "assets/Comodin.png"
    
    return portrayal

map_file = "data/mapa10x10.txt"
model = BombermanModel(map_file, "BFS", "Manhattan")
grid = CanvasGrid(agent_portrayal, model.grid_width, model.grid_height, 500, 500)
algorithm_choice = Choice("Algoritmo de búsqueda", value="BFS", choices=["BFS", "DFS", "UCS", "BS", "HC", "A*", "AlphaBeta"])
heuristic_choice = Choice("Heurística", value="Manhattan", choices=["Manhattan", "Euclidiana"])
#cambiar el rango por 0
jokers_choice = Choice("Número de comodines", value=3, choices=list(range(1, 11)))
server = ModularServer(BombermanModel, [grid], "Bomberman Model", {"map_file": map_file, "algorithm": algorithm_choice, 
                                                                   "heuristic": heuristic_choice, "jokers": jokers_choice})
server.port = 8521
server.launch()
