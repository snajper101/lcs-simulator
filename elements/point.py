from elements.track_elements import TrackElement
import time
from constants import Constants
from typing import List

class Point(TrackElement):
    def __init__(self, name: str, position: tuple, number: str = "", direction: str = "+"):
        super().__init__(name, position)
        self.direction = direction
        self.number = number
        self.occupied = False
        self.changing = False
        self.locked = False
        
        self.register_action("PLUS", self.set_direction_plus)
        self.register_action("MINUS", self.set_direction_minus)
        
    def set_direction_plus(self):
        if not self.locked and len(self.routes) == 0:
            self.start_move("+")
        
    def set_direction_minus(self):
        if not self.locked and len(self.routes) == 0:
            self.start_move("-")

    def start_move(self, new_direction: str):
        if self.direction != new_direction:
            self.target_direction = new_direction
            self.change_start_time = time.time()
            self.changing = True
            self.locked = True
            
    def update(self):
        if self.changing:
            if time.time() - self.change_start_time >= Constants.POINT_CHANGE_DELAY:
                self.direction = self.target_direction
                self.changing = False
                self.locked = False
                self.target_direction = None
        super().update()
        
    def __str__(self):
        return self.number