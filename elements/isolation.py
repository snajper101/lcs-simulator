from typing import List

class Isolation():
    def __init__(self, number: str) -> str:
        self.number = number.split("/")[0]
        
        self.route = None
        self.is_train_route = True
        
    def set_route(self, route):
        if not route:
            return
        self.route = route
        self.is_train_route = route.is_train_route