from elements.semaphore import Semaphore, SignalType
from elements.station import Station
from elements.point import Point
from elements.crossing import Crossing, CrossingState
from elements.line_blockade import LineBlockade
from elements.isolation import Isolation
from elements.route import Route
from typing import Dict, Tuple, Any, List
from maps import Maps
from constants import Constants
from collections.abc import Callable
class Simulator:
    def __init__(self):
        self.current_map_data = {}
        self.logical_elements = {}
        self.dependencies = {}
        self.signals = {}
        self.pending_tasks = []
    
    def load_map(self, selected_map: Maps) -> None:
        self.current_map_data = selected_map.schema
        self.dependencies = selected_map.dependencies
        self.logical_elements : Dict[ str, Any ] = {}
        repeater_signals: List[ Point ] = []
        self.signals: Dict[ str, Semaphore ] = {}
        self.isolations: Dict[ str, Isolation ] = {}
        self.points: Dict[ str, Point ] = {}
        self.crossings : Dict[str, Crossing] = {}
        
        for coord_str, elements in self.current_map_data.items():
            grid_pos = tuple(map(int, coord_str.split('-')))
            for element in elements:
                name = element.get("Name", "")
                labels = element.get("TextLabels")
                if "TextLabels" in element and labels:
                    number = labels.get( "Number", labels.get("Index", labels.get("ID")) )
                    if isolation_name := labels.get("IsolationName"):
                        isolation = Isolation(isolation_name)
                        self.isolations[isolation.number] = isolation
                if "Sem" in name:
                    self.logical_elements[coord_str] = Semaphore(name, grid_pos, SignalType.SEMI_AUTO, number, self)
                    self.signals[number] = self.logical_elements[coord_str]
                elif "To_" in name:
                    self.logical_elements[coord_str] = Semaphore(name, grid_pos, SignalType.REPEATER, number, self)
                    repeater_signals.append(self.logical_elements[coord_str])
                elif "TrainEnd" in name:
                    self.logical_elements[coord_str] = Semaphore(name, grid_pos, SignalType.EXIT, number, self)
                    self.signals[number] = self.logical_elements[coord_str]
                elif "Point" in name:
                    self.logical_elements[coord_str] = Point(name, grid_pos, labels.get("Number"), labels.get("MainDirection"))
                    self.points[number] = self.logical_elements[coord_str]
                elif "LineBlockNew" in name:
                    self.logical_elements[coord_str] = LineBlockade(name, grid_pos, labels.get("Direction"), labels.get("Type"))
                elif labels: 
                    if crossing_id := labels.get("CrossingID"):
                        if not crossing_id in self.crossings:
                            self.crossings[crossing_id] = Crossing(name, grid_pos)
                        self.logical_elements[coord_str] = self.crossings[ crossing_id ]
                    
        signal : Semaphore
        for coord_str, signal in self.signals.items():
            signal.load_routes(self.dependencies.get(signal.number, {}), self.signals.values())
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
    
    def create_route(self, semaphore : Semaphore, end_semaphore: Semaphore, route : Route, is_train : bool) -> bool:
        for isolation in route.isolations:
            if isolation.route is not None:
                return False
            
        wait_time = 0    
        
        for crossing in route.crossings:
            if crossing.state == CrossingState.OPENED:
                wait_time = max(Constants.CROSSING_CHANGE_DELAY, wait_time)
                crossing.close_crossing()
                
        for direction, point in route.points:
            if point.direction != direction:
                if direction == "PLUS":
                    point.set_direction_plus()
                else:
                    point.set_direction_minus()
                wait_time = max(Constants.POINT_CHANGE_DELAY, wait_time)
            
        def finalize_route():
            for isolation in route.isolations:
                isolation.set_route(route)
            for direction, point in route.points:
                point.add_route(route)
            for crossing in route.crossings:
                crossing.add_route(route)
            semaphore.accept_route(route)
            end_semaphore.accept_ending_route(route)

        self.delay_action(wait_time, finalize_route)
        
        return True
        
    def update(self, dt):
        for element in self.logical_elements.values():
            element.update()
            
        for task in self.pending_tasks[:]:
            task["timer"] -=  dt
            if task["timer"] <= 0:
                task["action"]()
                self.pending_tasks.remove(task)
                
    def delay_action(self, delay_seconds: float, action_function: Callable):
        if delay_seconds <= 0:
            action_function()
        else:
            self.pending_tasks.append({
                "timer": delay_seconds,
                "action": action_function,
            })