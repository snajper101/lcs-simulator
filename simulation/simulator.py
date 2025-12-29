from elements.semaphore import Semaphore, SignalType
from elements.station import Station
from elements.point import Point
from elements.crossing import Crossing
from typing import Dict
class Simulator:
    def __init__(self):
        self.current_map_data = {}
        self.logical_elements = {}
    
    def load_map(self, map_data : Dict ) -> None:
        self.current_map_data = map_data
        self.logical_elements = {}
        repeater_signals = []
        signals = {}
        
        for coord_str, elements in map_data.items():
            grid_pos = tuple(map(int, coord_str.split('-')))
            for element in elements:
                name = element.get("Name", "")
                if "TextLabels" in element:
                    labels = element["TextLabels"]
                    number = labels.get( "Number", labels.get("Index") )
                if "Sem" in name:
                    self.logical_elements[ coord_str ] = Semaphore(name, grid_pos, SignalType.SEMI_AUTO, number)
                    signals[ number ] = self.logical_elements[ coord_str ]
                if "To_" in name:
                    self.logical_elements[ coord_str ] = Semaphore(name, grid_pos, SignalType.REPEATER, number)
                    repeater_signals.append(self.logical_elements[ coord_str ])
                elif "Point" in name:
                    self.logical_elements[ coord_str ] = Point(name, grid_pos)
                elif "Crossing" in name:
                    self.logical_elements[ coord_str ] = Crossing(name, grid_pos)
                    
        signal : Semaphore
        for signal in repeater_signals:
            advance_signal = signal.number
            if advance_signal_ref := signals.get(advance_signal.replace("To", "")):
                signal.set_advance_signal( advance_signal_ref )
    
    def update(self, dt):
        pass