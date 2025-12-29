from enum import Enum
from elements.track_elements import TrackElement

class SignalState(Enum):
    S1 = 0
    S2 = 1
    
class SignalType(Enum):
    AUTO = 0
    SEMI_AUTO = 1
    REPEATER = 2

class Semaphore(TrackElement):
    def __init__(self, name: str, position: tuple, signal_type: SignalType, number: str):
        super().__init__(name, position)
        self.state = SignalState.S1
        self.signal_type = signal_type
        self.is_shunt_signal = "Shunt" in name
        self.number = number
        
    def set_advance_signal(self, advance_signal: "Semaphore" ):
        self.advance_signal = advance_signal

    def set_state(self, new_state: SignalState):
        self.state = new_state
        
    def __str__(self):
        return self.number