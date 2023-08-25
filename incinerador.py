from mesa import Agent, Model
from mesa.space import SingleGrid
from mesa.time import RandomActivation
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import Checkbox
from mesa.visualization.UserParam import Slider


import heapq # Librería para el método de búsquda del camino más corto A*

class Agentes(Agent):
    def __init__(self, model, pos):
        super().__init__(model.next_id(), model)
        self.pos = pos

    def step(self):
        if not hasattr(self, 'path') or not self.path:
            self.path = astar(self.model.matrix, self.pos, self.model.ghost_target_pos)

        if self.path:
            next_position = self.path.pop(0)
            self.model.grid.move_agent(self, next_position)


class Incinerador(Agent):
    def __init__(self, model, pos):
        super().__init__(model.next_id(), model)
        self.pos = pos


#def place_wall_blocks(model, matrix):
#    for x in range(model.grid.width):
#        for y in range(model.grid.height):
#            if matrix[y][x] == 0:
#                block = WallBlock(model, (x, y))
#                model.grid.place_agent(block, (x, y))


class   Sala(Model):
    def getGridSize(self):
        return self.grid.width, self.grid.height
    
    def __init__(self, trash=0.45, grid_size=None):
        super().__init__()
        
        if grid_size:
            self.grid = SingleGrid(81, 81, torus=False)
        else:
            self.grid = SingleGrid(51, 51, torus=False)
        self.schedule = RandomActivation(self)

        #self.ghost_target_pos = (3, 1)  # Posición objetivo para el fantasma

        robot1 = Agentes(self, (0, 0))
        self.grid.place_agent(robot1, robot1.pos)
        self.schedule.add(robot1)
        
        robot2 = Agentes(self, (0, 50))  
        self.grid.place_agent(robot2, robot2.pos)
        self.schedule.add(robot2)

        robot3 = Agentes(self, (50, 0))  
        self.grid.place_agent(robot3, robot3.pos)
        self.schedule.add(robot3)

        robot4 = Agentes(self, (50, 50))  
        self.grid.place_agent(robot4, robot4.pos)
        self.schedule.add(robot4)
        
        robot5 = Agentes(self, (27, 27))  
        self.grid.place_agent(robot5, robot5.pos)
        self.schedule.add(robot5)
        
        incinerador = Incinerador(self, (26, 26))  
        self.grid.place_agent(incinerador, incinerador.pos)
        self.schedule.add(incinerador)
       
    def step(self):
        self.schedule.step()


##### Búsqueda del camino más corto #####
class Node: # Clase nodo
    def __init__(self, position, parent=None):
        self.position = position
        self.parent = parent
        self.g = 0
        self.h = 0
        self.f = 0

    def __lt__(self, other):
        return self.f < other.f

def astar(grid, start, end): # A*
    open_list = []
    closed_set = set()

    start_node = Node(start)
    end_node = Node(end)
    
    heapq.heappush(open_list, start_node)

    while open_list:
        current_node = heapq.heappop(open_list)

        if current_node.position == end_node.position:
            path = []
            while current_node:
                path.append(current_node.position)
                current_node = current_node.parent
            return path[::-1]
        
        closed_set.add(current_node.position)

        for neighbor in get_neighbors(current_node.position, grid):
            if neighbor in closed_set:
                continue
            
            g_score = current_node.g + 1
            h_score = heuristic(neighbor, end_node.position)
            f_score = g_score + h_score

            if any(neighbor == node.position for node in open_list):
                existing_node = next(node for node in open_list if node.position == neighbor)
                if g_score < existing_node.g:
                    existing_node.g = g_score
                    existing_node.f = f_score
                    existing_node.parent = current_node
            else:
                neighbor_node = Node(neighbor, current_node)
                neighbor_node.g = g_score
                neighbor_node.h = h_score
                neighbor_node.f = f_score
                heapq.heappush(open_list, neighbor_node)

    return None

def get_neighbors(position, grid): #Obtiene los vecinos
    neighbors = []
    col, row = position  # Swap columna y fila
    rows, cols = len(grid), len(grid[0])

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for dc, dr in directions:  # Swap dc y dr 
        new_col, new_row = col + dc, row + dr  # Swap new_col and new_row 
        if 0 <= new_row < rows and 0 <= new_col < cols and grid[new_row][new_col] == 1:
            neighbors.append((new_col, new_row))  # Swap new_col and new_row 
    
    return neighbors

def heuristic(position, goal):
    return abs(position[0] - goal[0]) + abs(position[1] - goal[1])
##################


def agent_portrayal(agent):
    if type(agent) == Agentes:
        return {"Shape": "robot.png", "Layer": 0} # Si el agente es el fantasma
    elif type(agent) == Incinerador:
        return {"Shape": "circle", "r": 0.8, "Filled": "true", "Color": "Brown", "Layer": 0}
    else:
        return None  # Retorna None para agentes que no tienen representación visual

(gridSizeX, gridSizeY)=Sala().getGridSize()

print("Grid size X: ", gridSizeX, ",y:", gridSizeY)

grid = CanvasGrid(agent_portrayal, gridSizeX, gridSizeY, 700, 700)
server = ModularServer(Sala, [grid], "Robots Limpiadores", {
    "trash": Slider("Trash Density", 0.45, 0.01, 1.0, 0.01),
    "grid_size": Checkbox("Grid size (Off=51 On=81)", False),
})
server.port = 8522
server.launch()
