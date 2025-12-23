class Simulator:
    def __init__(self):
        self.current_map_data = {}
    
    def load_map(self, map_data : dict ) -> None:
        self.current_map_data = map_data
    
    def update(self, dt):
        pass