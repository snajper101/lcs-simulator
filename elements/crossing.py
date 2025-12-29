from enum import Enum
from elements.track_elements import TrackElement

class CrossingState(Enum):
    CLOSED = 0
    CLOSING = 1
    OPENED = 2
    OPENING = 3

class Crossing(TrackElement):
    def __init__(self, name: str, position: tuple):
        super().__init__(name, position)
        self.state = CrossingState.OPENED

    def set_state(self, new_state: CrossingState):
        self.state = new_state