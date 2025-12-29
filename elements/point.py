from elements.track_elements import TrackElement

class Point(TrackElement):
    def __init__(self, name: str, position: tuple, number: str = "", direction: str = "+"):
        super().__init__(name, position)
        self.direction = direction
        self.number = number
        self.locked = False
