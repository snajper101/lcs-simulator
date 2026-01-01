from enum import Enum
from elements.track_elements import TrackElement
from typing import Dict, Tuple, List
from elements.route import Route
class SignalState(Enum):
    S1 = 0
    S2 = 1
    
class SignalType(Enum):
    AUTO = 0
    SEMI_AUTO = 1
    REPEATER = 2
    EXIT = 3

class Semaphore(TrackElement):
    def __init__(self, name: str, position: Tuple, signal_type: SignalType, number: str, simulator):
        super().__init__(name, position)
        self.state = SignalState.S1
        self.signal_type = signal_type
        self.is_shunt_signal = "Shunt" in name
        self.number = number
        self.advance_selected = None
        self.routes : List[Route] = []
        self.active_route : Route = None
        self.ending_route : Route = None
        self.simulator = simulator
        
        if "SemOnlyTrain" in name:
            self.register_action("PRZEBIEG POCIĄGOWY", self.create_train_route)
        elif "SemOnlyShunt" in name:
            self.register_action("PRZEBIEG MANEWROWY", self.create_shunt_route)
        else:
            self.register_action("PRZEBIEG POCIĄGOWY", self.create_train_route)
            self.register_action("PRZEBIEG MANEWROWY", self.create_shunt_route)
            
    def set_advance_signal(self, advance_signal: "Semaphore" ):
        self.advance_signal = advance_signal

    def set_state(self, new_state: SignalState):
        self.state = new_state
        
    def create_shunt_route(self):
        self.create_route(False)
    
    def create_train_route(self):
        self.create_route(True)
    
    def create_route(self, is_train : bool = True):
        selected_route : Route = self.get_selected_route()
        if not selected_route:
            return
        self.simulator.create_route(self, selected_route.advance_signal, selected_route, is_train)
    
    def set_advance_selected_signal(self, advance_selected: "Semaphore"):
        self.advance_selected = advance_selected
        
    def get_selected_route(self) -> Route | None:
        if not self.advance_selected:
            return None
        for route in self.routes:
            if route.advance_signal == self.advance_selected:
                return route
        return None
    
    def load_routes(self, dependencies: Dict, signals: List["Semaphore"]):
        first = lambda x : x[0] if x else None
        for route in dependencies:
            self.routes.append(Route(route, self, first([signal for signal in signals if signal.number == route[3]]), self.simulator))
        
    def accept_route(self, route: Route):
        self.state = SignalState.S2
        self.active_route = route
        self.register_action("ZW", self.cancel_route)
        
    def accept_ending_route(self, route: Route):
        self.ending_route = route
        
    def cancel_route(self) -> None:
        if not self.active_route:
            return
        
    def __str__(self):
        return self.number