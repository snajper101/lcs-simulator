from elements.semaphore import Semaphore, SignalType
from elements.station import Station
from elements.point import Point
from elements.crossing import Crossing
from typing import Dict, Tuple, Any, List
class Simulator:
    def __init__(self):
        self.current_map_data = {}
        self.logical_elements = {}
        self.signals = {}
    
    def load_map(self, map_data : Dict ) -> None:
        self.current_map_data = map_data
        self.logical_elements : Dict[ str, Any ] = {}
        repeater_signals: List[ Point ] = []
        self.signals: Dict[ str, Semaphore ] = {}
        crossings : Dict[str, Crossing] = {}
        
        for coord_str, elements in map_data.items():
            grid_pos = tuple(map(int, coord_str.split('-')))
            for element in elements:
                name = element.get("Name", "")
                labels = element.get("TextLabels")
                if "TextLabels" in element and labels:
                    number = labels.get( "Number", labels.get("Index") )
                if "Sem" in name:
                    self.logical_elements[ coord_str ] = Semaphore(name, grid_pos, SignalType.SEMI_AUTO, number)
                    self.signals[ number ] = self.logical_elements[ coord_str ]
                if "To_" in name:
                    self.logical_elements[ coord_str ] = Semaphore(name, grid_pos, SignalType.REPEATER, number)
                    repeater_signals.append(self.logical_elements[ coord_str ])
                elif "Point" in name:
                    self.logical_elements[ coord_str ] = Point(name, grid_pos)
                elif labels: 
                    if crossing_id := labels.get("CrossingID"):
                        if not crossing_id in crossings:
                            crossings[ crossing_id ] = Crossing(name, grid_pos)
                        self.logical_elements[ coord_str ] = crossings[ crossing_id ]
                    
        signal : Semaphore
        for signal in repeater_signals:
            advance_signal = signal.number
            if advance_signal_ref := self.signals.get(advance_signal.replace("To", "")):
                signal.set_advance_signal( advance_signal_ref )
    
    def get_map_object_by_name(self, object_name : str) -> Dict:
        if self.current_map_data is None:
            return {}
        found_objects = {}
        for coord_str, elements in self.current_map_data.items():
            for element in elements:
                name = element.get("Name", "")
                if name == object_name:
                    found_objects[ coord_str ] = element
                    break
        return found_objects
    
    def select_crossing_object_by_id(self, crossing_object : str, crossing_id: str) -> Tuple:
        crossings = self.get_map_object_by_name(crossing_object)

        for position, object in crossings.items():
            if object.get("TextLabels", {}).get("CrossingID") == crossing_id:
                return position, object

        return None
        
    def update(self):
        for element in self.logical_elements.values():
            element.update()