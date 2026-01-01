from collections.abc import Callable

class TrackElement:
    def __init__(self, name: str, position: tuple ) -> None:
        self.name = name
        self.position = position
        self.actions = {}
        self.locked = False
        self.routes = []
        
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