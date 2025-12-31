from enum import Enum
from elements.track_elements import TrackElement
import time
from constants import Constants
class CrossingState(Enum):
    CLOSED = 0
    OPENED = 1

class Crossing(TrackElement):
    def __init__(self, name: str, position: tuple):
        super().__init__(name, position)
        self.state = CrossingState.OPENED
        self.changing = False
        self.locked = False
        
        self.register_action("OPEN", self.open_crossing)
        self.register_action("CLOSE", self.close_crossing)
        
    def open_crossing(self):
        if not self.locked:
            self.start_move(CrossingState.OPENED)
        
    def close_crossing(self):
        if not self.locked:
            self.start_move(CrossingState.CLOSED)

    def start_move(self, new_state: CrossingState):
        if self.state != new_state:
            self.target_state = new_state
            self.change_start_time = time.time()
            self.changing = True
            self.locked = True
            
    def update(self):
        if self.changing:
            if time.time() - self.change_start_time >= Constants.CROSSING_CHANGE_DELAY:
                self.state = self.target_state
                self.changing = False
                self.locked = False
                self.target_state = None
        super().update()