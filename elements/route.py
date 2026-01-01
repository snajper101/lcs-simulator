from typing import List, Dict, Tuple
from elements.crossing import Crossing
from elements.point import Point
from elements.isolation import Isolation

class Route():
    def __init__(self, route_str: str, start_signal, advance_signal, simulator) -> None:
        self.dependencies : List[str] = route_str[0]
        self.isolations_str : List[str] = route_str[1]
        self.speed_limit : int = route_str[2]
        self.start_signal = start_signal
        self.advance_signal = advance_signal
        self.is_train_route = True
        
        self.crossings : List[ Crossing ] = []
        self.points : List[ Tuple[str, Point]]= []
        for dependency in self.dependencies:
            if "Crossing" in dependency:
                if crossing_ref := simulator.crossings[dependency.replace("Crossing_", "")]:
                    self.crossings.append(crossing_ref)
            else:
                if point_ref := simulator.points[dependency.replace("+", "").replace("-", "")]:
                    self.points.append(("+" in dependency and "PLUS" or "MINUS", point_ref))
            
        self.isolations : List[Isolation] = []
        for isolation in self.isolations_str:
            if isolation in simulator.isolations:
                if isolation_ref := simulator.isolations[isolation]:
                    self.isolations.append(isolation_ref)
                    
    def is_occupied(self) -> bool:
        return False