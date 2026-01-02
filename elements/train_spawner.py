from elements.train import Train, MoveDirection
from elements.track import Track
from elements.line_blockade import BlocadeDirection
from typing import List, Tuple
from constants import Constants
import random

class TrainSpawner():
    def __init__(self, simulator, origin_name: str, possible_destinations: List[str], tracks: List[Track]):
        self.simulator = simulator
        self.waiting_trains : List[Train] = []
        self.origin_name: str = origin_name
        self.possible_destinations: List[str] = [destination for destination in possible_destinations if destination != origin_name]
        self.tracks : List[ Track ] = tracks
        
        self.spawn_timer = random.uniform(1, 2.0)
        self.min_delay = 5.0
        self.max_delay = 10.0
        
    def update(self, dt: float):
        self.spawn_timer -= dt
        if self.spawn_timer <= 0:
            self.spawn_train()
            self.spawn_timer = random.uniform(self.min_delay, self.max_delay)
    
    def spawn_train(self):
        if len(self.waiting_trains) < Constants.MAX_WAITING_TRAINS:
            destination = random.choice(self.possible_destinations)
            self.waiting_trains.append(Train(destination))
        
    def add_train_to_line(self, train : Train, track : Track):
        if track.line_block.state == ( track.direction == "Left" and BlocadeDirection.LEFT or BlocadeDirection.RIGHT) and not track.isolation.is_occupied() and len(track.isolation.occuping_trains) == 0:
            if train in self.waiting_trains:
                self.waiting_trains.remove(train)
                
                grid_x, grid_y = track.position
            
                if track.direction == "Left":
                    train.position = (float((grid_x + 1 ) * Constants.TILE_SIZE - 1), float(grid_y * Constants.TILE_SIZE + Constants.TILE_SIZE // 2))
                else:
                    train.position = (float(grid_x * Constants.TILE_SIZE), float(grid_y * Constants.TILE_SIZE + Constants.TILE_SIZE // 2))
                train.set_spawn_direction([track.direction == "Left" and MoveDirection.LEFT or MoveDirection.RIGHT])
                train.spawned = True
                
                self.simulator.add_active_train(train)
                   