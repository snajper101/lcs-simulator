from collections.abc import Callable
from elements.train import Train
from typing import List, Tuple

class TrackElement:
    def __init__(self, name: str, position: Tuple ) -> None:
        self.name = name
        self.position = position
        self.actions = {}
        self.locked = False
        self.routes = []
        self.reserved_routes = []
        self.occuping_trains : List[ Train ] = []
        self.movable : bool = True
        
    def register_action(self, name: str, func : Callable) -> None:
        self.actions[name] = func
        
    def execute_action(self, name: str) -> None:
        if self.locked:
            return
        if name in self.actions:
            self.actions[name]()
            
    def update(self):
        pass
        
    def add_route(self, route):
        self.routes.append(route)
        if route in self.reserved_routes:
            self.reserved_routes.remove(route)
        
    def remove_route(self, route):
        if route in self.routes:
            self.routes.remove(route)
        if route in self.reserved_routes:
            self.reserved_routes.remove(route)
    
    def reserve_route(self, route):
        if not route in self.reserved_routes:
            self.reserved_routes.append(route)
        
    def unreserve_route(self, route):
        if route in self.reserved_routes:
            self.reserved_routes.remove(route)
        
    def is_occupied(self) -> bool:
        return len(self.routes) > 0 or len(self.reserved_routes) > 0
    
    def add_train(self, train: Train):
        if not train in self.occuping_trains:
            self.occuping_trains.append(train)
        
    def remove_train(self, train: Train):
        if train in self.occuping_trains:
            self.occuping_trains.remove(train)
            for route in self.routes:
                self.remove_route(route)