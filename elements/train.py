from typing import Tuple, List
from constants import Constants, MoveDirection
import math
import random
from enum import Enum

class TrainType(Enum):
    PASSENGER = 0,
    CARGO = 1,
    HIGH_SPEED = 2

class Train():
    def __init__(self, destination: str):
        self.position : Tuple[float, float] = (0.0, 0.0)
        self.destination : str = destination
        self.spawned : bool = False
        self.train_type : TrainType = TrainType.PASSENGER
        self.max_speed : int = 120
        self.speed_limit : int | None = None
        self.move_directions : List[MoveDirection] = []
        self.default_direction: MoveDirection = None
        self.train_number : str = self.generate_train_number() 
        self.last_grid_pos : str | None = None
        self.advance_grid_pos : str | None = None
        self.delay = False
        self.last_update_time = 0
        
    def generate_train_number(self) -> str:
        if self.train_type == TrainType.PASSENGER:
            return str(random.randint(10000, 99999))
        elif self.train_number == TrainType.CARGO:
            return str(random.randint(100000, 999999))
        else:
            return str(random.randint(1000, 9999))
        
    def get_max_delay(self) -> float:
        if self.train_type == TrainType.PASSENGER:
            return 20
        elif self.train_number == TrainType.CARGO:
            return 45
        else:
            return 10
        
    def get_delay_cost(self) -> float:
        if self.train_type == TrainType.PASSENGER:
            return 2
        elif self.train_number == TrainType.CARGO:
            return 1
        else:
            return 5
        
    def set_spawn_direction(self, directions : List[MoveDirection]):
        self.move_directions = directions
        self.default_direction = directions[0]
        
    def get_current_speed(self) -> int:    
        if self.speed_limit:
            return min(self.max_speed, self.speed_limit)
        else:
            return self.max_speed
        
    def deduce_move_direction_from_point(self, point):
        if point.direction != "-":
            return
        if "South" in point.name:
            if not MoveDirection.BOTTOM in self.move_directions and not MoveDirection.UP in self.move_directions:
                self.move_directions.append(MoveDirection.BOTTOM)
        elif "North" in point.name:
            if not MoveDirection.BOTTOM in self.move_directions and not MoveDirection.UP in self.move_directions:
                    self.move_directions.append(MoveDirection.UP)
        if "East" in point.name:
            if not MoveDirection.RIGHT in self.move_directions and not MoveDirection.LEFT in self.move_directions:
                self.move_directions.append(MoveDirection.RIGHT)
        elif "West" in point.name:
            if not MoveDirection.RIGHT in self.move_directions and not MoveDirection.LEFT in self.move_directions:
                self.move_directions.append(MoveDirection.LEFT)        
        
    def deduce_move_direction_from_vertical_isolation(self):
        if MoveDirection.LEFT in self.move_directions:
            self.move_directions.remove(MoveDirection.LEFT)
        if MoveDirection.RIGHT in self.move_directions:
            self.move_directions.remove(MoveDirection.RIGHT)
            
    def deduce_move_direction_from_curve(self, element_name: str):
        if MoveDirection.UP in self.move_directions:
            if not self.default_direction in self.move_directions:
                self.move_directions.append(self.default_direction)
        elif "West" in element_name and not MoveDirection.BOTTOM in self.move_directions:
            self.move_directions.append(MoveDirection.BOTTOM)
        
    def calculate_advance_grid_pos(self, grid_pos: str) -> str | None:
        try:
            grid_x, grid_y = map(int, grid_pos.split('-'))
        except ValueError:
            return "0-0"

        for direction in self.move_directions:
            if direction == MoveDirection.LEFT:
                grid_x -= 1
            elif direction == MoveDirection.RIGHT:
                grid_x += 1
            elif direction == MoveDirection.UP:
                grid_y -= 1
            elif direction == MoveDirection.BOTTOM:
                grid_y += 1
        return f"{grid_x}-{grid_y}"
        
    def get_next_position(self, dt: float, offset: int = 0) -> Tuple[int, int]:
        directions_count = len(self.move_directions)
        position = self.position
        speed : float = dt * self.get_current_speed() * Constants.TRAIN_MOVE_SPEED * (1 / math.sqrt(directions_count) )
        for direction in self.move_directions:
            if direction == MoveDirection.LEFT:
                position = (position[0] - speed - offset * Constants.TILE_SIZE, position[1])
            elif direction == MoveDirection.RIGHT:
                position = (position[0] + speed + offset * Constants.TILE_SIZE, position[1])
            elif direction == MoveDirection.UP:
                position = (position[0], position[1] - speed - offset * Constants.TILE_SIZE)
            elif direction == MoveDirection.BOTTOM:
                position = (position[0], position[1] + speed + offset * Constants.TILE_SIZE) 
                
        return position       
                
    def update(self, simulator, position: Tuple[int, int], dt: float):
        if not self.spawned:
            return
        if position == self.position:
            self.last_update_time += dt
        else:
            self.last_update_time = 0
            self.delay = False
        self.position = position
        if not self.delay and self.last_update_time > self.get_max_delay():
            simulator.user_points -= self.get_delay_cost() 
            print("TEST")
            self.delay = True
    
    def destroy(self):
        pass
        
    def __str__(self) -> str:
        return self.train_number