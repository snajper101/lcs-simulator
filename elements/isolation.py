from typing import List
from elements.train import Train
class Isolation():
    def __init__(self, name: str, number: str) -> str:
        self.name = name
        self.number = number.split("/")[0]
        
        self.route = None
        self.reserved_route = None
        self.is_train_route = True
        self.occuping_trains : List[Train] = []
        
    def set_route(self, route):
        if not route:
            return
        self.route = route
        self.reserved_route = None
        self.is_train_route = route.is_train_route
        
    def remove_route(self):
        self.route = None
        self.reserved_route = None
        
    def reserve_route(self, route):
        self.reserved_route = route
        
    def unreserve_route(self):
        self.reserved_route = None
        
    def is_occupied(self) -> bool:
        return self.route is not None or self.reserved_route is not None
    
    def add_train(self, train: Train):
        if not train in self.occuping_trains:
            self.occuping_trains.append(train)
        
    def remove_train(self, train: Train):
        if train in self.occuping_trains:
            self.occuping_trains.remove(train)
        self.remove_route()
        
    def __str__(self) -> str:
        return self.number