from mesa import Agent, Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import Checkbox
from mesa.visualization.UserParam import Slider
from mesa.visualization.modules import ChartModule
import numpy as np


import heapq # Librería para el método de búsquda del camino más corto A*

class Agentes(Agent):
    w_trash=False
    def __init__(self, model, pos):
        super().__init__(model.next_id(), model)
        self.pos = pos

    def step(self):
        if self.w_trash==False:
            new_pos = self.pos + np.array([self.random.randrange(-1, 2, 1),self.random.randrange(-1,2,1)])
            while (self.model.grid.out_of_bounds(new_pos)) :
                        new_pos = self.pos + np.array([self.random.randrange(-1, 2, 1),self.random.randrange(-1,2,1)])
            Incinerador.ON = False
            self.model.grid.move_agent(self, new_pos)
        else:
            new_pos = self.pos
            if (self.pos[0] != ((self.model.grid.width-2)//2)) or (self.pos[1] != ((self.model.grid.height-2)//2)):
                  # Inicializar new_pos con la posición actual
                
                if self.pos[0] < ((self.model.grid.width - 2) // 2):
                    new_pos = new_pos + np.array([1, 0])
                elif self.pos[0] > ((self.model.grid.width - 2) // 2):
                    new_pos = new_pos + np.array([-1, 0])
                
                if self.pos[1] < ((self.model.grid.height - 2) // 2):
                    new_pos = new_pos + np.array([0, 1])
                elif self.pos[1] > ((self.model.grid.height - 2) // 2):
                    new_pos = new_pos + np.array([0, -1])
                        
                elif self.pos[0] == ((self.model.grid.width-2)//2):
                    if self.pos[1] < ((self.model.grid.height-2)//2):
                        new_pos = self.pos + np.array([0,1])
                    elif self.pos[1] > ((self.model.grid.height-2)//2):
                        new_pos = self.pos + np.array([0,-1])
                
                elif self.pos[1] == ((self.model.grid.height-2)//2):
                    if self.pos[0] < ((self.model.grid.width-2)//2):
                        new_pos = self.pos + np.array([1,0])
                    elif self.pos[0] > ((self.model.grid.width-2)//2):
                        new_pos = self.pos + np.array([-1,0])
                
            else:
               self.w_trash=False
               Incinerador.ON = True
               
            self.model.grid.move_agent(self, new_pos)

        for element in self.model.grid.get_cell_list_contents([self.pos]):
            if type(element) == Basura and self.w_trash==False:
                self.model.grid.remove_agent(element)
                self.model.schedule.remove(element)
                self.w_trash=True

class Incinerador(Agent):
    def __init__(self, model, pos):
        super().__init__(model.next_id(), model)
        self.pos = pos
        self.ON = False
        
class Basura(Agent):
    
    def __init__(self, model):
        super().__init__(model.next_id(), model)
        

class   Sala(Model):
    def getGridSize(self):
        return self.grid.width, self.grid.height
    
    def __init__(self, density=0.45, grid_size=False, max_steps=1000):
        super().__init__()
        
        if grid_size:
            self.grid = MultiGrid(51, 51, torus=False)
        else:
            self.grid = MultiGrid(21, 21, torus=False)
        self.schedule = RandomActivation(self)
        self.max_steps = max_steps
        
        print(self.grid.width, self.grid.height)

        #self.ghost_target_pos = (3, 1)  # Posición objetivo para el fantasma
        for _,(x,y) in self.grid.coord_iter():
            if (x,y) == (0,0):
                robot1 = Agentes(self, (0, 0))
                self.grid.place_agent(robot1, robot1.pos)
                self.schedule.add(robot1)
                
            elif (x,y) == (0,self.grid.height - 1):
                robot2 = Agentes(self, (0, self.grid.height - 1))  
                self.grid.place_agent(robot2, robot2.pos)
                self.schedule.add(robot2)
                

            elif (x,y) == (self.grid.width-1,0):
                robot3 = Agentes(self, (self.grid.width-1, 0))  
                self.grid.place_agent(robot3, robot3.pos)
                self.schedule.add(robot3)
                

            elif (x,y) == (self.grid.width-1, self.grid.height-1):
                robot4 = Agentes(self, (self.grid.width-1, self.grid.height-1))  
                self.grid.place_agent(robot4, robot4.pos)
                self.schedule.add(robot4)
                
            
            elif (x,y) == ((self.grid.width-1)//2, (self.grid.height-1)//2):    
                robot5 = Agentes(self, ((self.grid.width-1)//2, (self.grid.height-1)//2))  
                self.grid.place_agent(robot5, robot5.pos)
                self.schedule.add(robot5)
                
            elif (x,y) == ((self.grid.width-2)//2, (self.grid.height-2)//2):     
                incinerador = Incinerador(self, ((self.grid.width-2)//2, (self.grid.height-2)//2))  
                self.grid.place_agent(incinerador, incinerador.pos)
                self.schedule.add(incinerador)
                
            elif self.random.random() < density:
                basura = Basura(self)
                self.grid.place_agent(basura, (x,y))
                self.schedule.add(basura)

       
    def step(self):
        if self.schedule.time < self.max_steps:
            self.schedule.step()
            print(Incinerador.ON)

def agent_portrayal(agent):
    if type(agent) == Agentes:
        return {"Shape": "robot.png", "Layer": 0} # Si el agente es el fantasma
    elif type(agent) == Incinerador:
        return {"Shape": "circle", "r": 0.8, "Filled": "true", "Color": "Brown", "Layer": 0}
    elif type(agent) == Basura:
        return {"Shape": "circle", "Filled": "true", "Color": "Gray", "r": 0.75, "Layer": 0}
    else:
        return None  # Retorna None para agentes que no tienen representación visual


grid = CanvasGrid(agent_portrayal, 51, 51, 700, 700)

chart = ChartModule([{"Label": "Trash", "Color": "Black"}])

server = ModularServer(Sala, [grid], "Robots Limpiadores", {
    "density": Slider("Trash density", 0.50, 0.01, 1.0, 0.01),
    "max_steps": Slider("Max Step", 1000, 1, 1000, 1),
    "grid_size": Checkbox("Grid size (Off=21 On=51)", False),
})
server.port = 8522
server.launch()

