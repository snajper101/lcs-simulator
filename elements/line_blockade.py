from enum import Enum
from elements.track_elements import TrackElement
import time
from constants import Constants
class BlocadeDirection(Enum):
    IDLE = 0
    LEFT = 1
    RIGHT = 2

class LineBlockade(TrackElement):
    def __init__(self, name: str, position: tuple, direction: str, type: str):
        super().__init__(name, position)
        self.state = BlocadeDirection.IDLE
        self.default_direction = direction == "Left" and BlocadeDirection.LEFT or BlocadeDirection.RIGHT
        self.type = type
        self.changing = False
        self.previous_direction = None

        self.register_action("WBL", self.set_direction)
        self.register_action("ZWBL", self.reset_direction)

    def reset_direction(self):
        if self.state == BlocadeDirection.IDLE:
            return
        self.previous_direction = self.state
        self.start_move(BlocadeDirection.IDLE)
        
    
    def set_direction(self):
        if self.state != BlocadeDirection.IDLE:
            return
        if not self.previous_direction:
            self.start_move(self.default_direction)
        else:
            self.start_move(self.previous_direction == BlocadeDirection.LEFT and BlocadeDirection.RIGHT or BlocadeDirection.LEFT)
        
    def start_move(self, new_direction: BlocadeDirection):
        if self.state != new_direction:
            self.target_state = new_direction
            self.change_start_time = time.time()
            self.changing = True
            self.locked = True
            
    def update(self):
        if self.changing:
            if time.time() - self.change_start_time >= Constants.BLOCKADE_CHANGE_DELAY:
                self.state = self.target_state
                self.changing = False
                self.locked = False
                self.target_state = None
        super().update()