from mesa import Agent

from agents.fire import Fire
from agents.metal import Metal


class Bomb(Agent):
    def __init__(self, unique_id, pos, model, power):
        super().__init__(unique_id, model)
        self.pos = pos
        self.timer = power + 2  # Tiempo hasta la explosión
        self.power = power
        self.exploded = False  # Para controlar si la bomba ha explotado

    def step(self):
        # Reducir el temporizador en cada paso
        if not self.exploded:
            self.timer -= 1
            if self.timer <= 0:
                self.explode()

    def explode(self):
        # Marcar la bomba como explotada
        self.exploded = True
        # Generar las posiciones afectadas por la explosión
        explosion_positions = [self.pos]
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            for i in range(1, self.power + 1):
                x, y = self.pos[0] + dx * i, self.pos[1] + dy * i
                if not (0 <= x < self.model.grid_width and 0 <= y < self.model.grid_height):
                    break
                explosion_positions.append((x, y))
                
                # Detener la explosión si encuentra un bloque de metal
                cell_contents = self.model.grid.get_cell_list_contents((x, y))
                if any(isinstance(obj, Metal) for obj in cell_contents):
                    break

        # Crear un marcador de explosión para cada posición afectada
        for pos in explosion_positions:
            fire_marker = Fire(self.model.next_id(), pos, self.model)
            self.model.grid.place_agent(fire_marker, pos)
            self.model.schedule.add(fire_marker)

        # Eliminar la bomba del modelo después de explotar
        self.model.grid.remove_agent(self)
        self.model.schedule.remove(self)