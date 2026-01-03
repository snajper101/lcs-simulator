from elements.semaphore import Semaphore, SignalType, SignalState
from elements.station import Station
from elements.point import Point
from elements.crossing import Crossing, CrossingState
from elements.line_blockade import LineBlockade, BlocadeDirection
from elements.isolation import Isolation
from elements.route import Route
from elements.train_spawner import TrainSpawner
from elements.track import Track
from elements.train import Train
from typing import Dict, Tuple, Any, List
from maps import Maps
from constants import Constants, MoveDirection
from collections.abc import Callable
import math
class Simulator:
    def __init__(self):
        self.current_map_data : Dict = {}
        self.logical_elements : Dict[str, Any] = {}
        self.dependencies : Dict = {}
        self.signals : Dict[str, Semaphore] = {}
        self.pending_tasks : Callable = []
        self.active_trains : List[Train] = []
        self.user_points : int = 100
    
    def load_map(self, selected_map: Maps) -> None:
        self.current_map_data = selected_map.schema
        self.dependencies = selected_map.dependencies
        self.logical_elements : Dict[str, Any] = {}
        repeater_signals: List[Point] = []
        self.signals: Dict[str, Semaphore] = {}
        self.points: Dict[str, Point] = {}
        self.crossings : Dict[str, Crossing] = {}
        self.line_blocks : Dict[str, LineBlockade] = {}
        self.isolations : List[ Isolation ] = []
        
        train_spawners : List[ Tuple[str, str, str]] = []
        
        for coord_str, elements in self.current_map_data.items():
            grid_pos = tuple(map(int, coord_str.split('-')))
            for element in elements:
                name = element.get("Name", "")
                labels = element.get("TextLabels")
                if "TextLabels" in element and labels:
                    number = labels.get( "Number", labels.get("Index", labels.get("ID")) )
                    if isolation_name := labels.get("Number", labels.get("IsolationName")):
                        if element_size := element.get("Size"):
                            size = (element_size[0] // 50 , element_size[1] // 50 )
                            pass
                        else:
                            size = (1, 1)

                        isolation_ref = Isolation(name, isolation_name, labels.get("SBLName") != None)
                        self.isolations.append(isolation_ref)
                        for x in range(size[0]):
                            for y in range(size[1]):
                                self.logical_elements[f"{grid_pos[0] + x}-{grid_pos[1] + y}"] = isolation_ref
                
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
                    self.logical_elements[coord_str] = LineBlockade(name, grid_pos, labels.get("Direction"), labels.get("Type"), labels.get("BlockName"), labels.get("Number"))
                    self.line_blocks[number] = self.logical_elements[coord_str]
                elif "LineTrainSpawner" in name:
                    train_spawners.append((coord_str, element.get("Direction"), labels.get("Destination")))
                elif labels: 
                    if crossing_id := labels.get("CrossingID"):
                        if not crossing_id in self.crossings:
                            self.crossings[crossing_id] = Crossing(name, grid_pos)
                        self.logical_elements[coord_str] = self.crossings[crossing_id]

        self.train_sprawners: Dict[str, TrainSpawner] = {}
        destinations_left = [data[2] for data in train_spawners if data[1] == "Right" ]
        destinations_right = [data[2] for data in train_spawners if data[1] == "Left" ]
        for coord_str, direction, _ in train_spawners:    
            for spawner in self.current_map_data[coord_str]:
                tracks: List[Track] = []
                for track in spawner.get("Tracks", {}):
                    line_block = [block for block in self.line_blocks.values() if block.number == track["Name"]][0]
                    tracks.append(Track(track["Name"], track["Position"], track["Normal"], direction, line_block, self.logical_elements[track["Position"]]))
                labels = spawner.get("TextLabels", {})
                self.logical_elements[coord_str] = TrainSpawner(self, labels.get("Destination", ""), direction == "Left" and destinations_left or destinations_right, tracks)
                self.train_sprawners[coord_str] = self.logical_elements[coord_str]
                    
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
            if isolation.is_occupied():
                return False
            
        advance_signal : Semaphore
        if advance_signal := route.advance_signal:
            if "SBL" in advance_signal.number or "PBL" in advance_signal.number:
                block_name = advance_signal.number.split("_")[1]
                line_number = advance_signal.number.split("_")[2]
                block_refs = [block for block in self.line_blocks.values() if block.block_name == block_name and line_number in block.number ]
                for block in block_refs:
                    if block.state == BlocadeDirection.IDLE or \
                        ("East" in advance_signal.name and block.state == BlocadeDirection.LEFT) or \
                        ("West" in advance_signal.name and block.state == BlocadeDirection.RIGHT):
                        return False
            
        wait_time = 0    
        
        for isolation in route.isolations:
            isolation.reserve_route(route)
        
        for crossing in route.crossings:
            if crossing.state == CrossingState.OPENED:
                wait_time = max(Constants.CROSSING_CHANGE_DELAY, wait_time)
                crossing.close_crossing()
            crossing.reserve_route(route)
                
        for direction, point in route.points:
            if point.direction != direction:
                if direction == "PLUS":
                    point.set_direction_plus()
                else:
                    point.set_direction_minus()
                wait_time = max(Constants.POINT_CHANGE_DELAY, wait_time)
            point.reserve_route(route)
            
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
        
    def cancel_route(self, semaphore : Semaphore, end_semaphore: Semaphore, route : Route):
        for isolation in route.isolations:
            isolation.remove_route()
        
        for crossing in route.crossings:
            crossing.remove_route(route)
                
        for direction, point in route.points:
            point.remove_route(route)
            
        semaphore.cancel_route()
        end_semaphore.cancel_route()
        
    def add_active_train(self, train : Train):
        if not train in self.active_trains:
            self.active_trains.append(train)
        
    def remove_active_train(self, train : Train):
        if train in self.active_trains:
            destination = None
            for train_spawner in self.train_sprawners.values():
                for track in train_spawner.tracks:
                    for i in range(5):
                        finished = False
                        if f"{track.position[0] + (i * (MoveDirection.LEFT in train.move_directions and -1 or 1))}-{track.position[1]}" == train.last_grid_pos:
                            destination = train_spawner.origin_name
                            finished = True
                            break
                        if finished:
                            break
                if destination:
                    break
            train.destroy()
            if train.destination == destination:
                self.user_points += Constants.FINISHED_ROUTE_POINTS
            else:
                self.user_points -= Constants.WRONG_DESTINATION_PENALTY
            
            self.active_trains.remove(train)
        
    def get_element_at_grid_pos(self, grid_pos: str) -> Any:
        if grid_pos in self.logical_elements.keys():
            return self.logical_elements[grid_pos]
        else:
            return None
        
    def update(self, dt):
        for element in self.logical_elements.values():
            if isinstance(element, TrainSpawner):
                element.update(dt)
            elif hasattr(element, "update"):
                element.update()
            
        for task in self.pending_tasks[:]:
            task["timer"] -=  dt
            if task["timer"] <= 0:
                task["action"]()
                self.pending_tasks.remove(task)
                
        get_grid_post = lambda position : f"{math.floor(position[0] // Constants.TILE_SIZE)}-{math.floor(position[1] // Constants.TILE_SIZE)}"
        trains_to_remove : List[ Train ] = [] 
        for train in self.active_trains:
            advance_position = train.get_next_position(dt)
            
            if advance_position[0] < 0 or advance_position[1] < 0:
                if train.last_grid_pos:
                    if element := self.get_element_at_grid_pos(train.last_grid_pos):
                        if hasattr(element, "remove_train"):
                            element.remove_train(train) 
                trains_to_remove.append(train)
                continue
            
            grid_pos = get_grid_post(advance_position) 
            
            if grid_pos == train.advance_grid_pos:
                if element := self.get_element_at_grid_pos(grid_pos):
                    offset = 0
                    skip_train = False
                    while element:
                        if isinstance(element, Semaphore):
                            semaphore : Semaphore = element 
                            if semaphore.state == SignalState.S1 and semaphore.direction in train.move_directions and semaphore.signal_type in [SignalType.AUTO, SignalType.SEMI_AUTO]:
                                skip_train = True
                                break
                            elif semaphore.direction in train.move_directions:
                                semaphore.state = SignalState.S1
                                semaphore.active_route = None
                                semaphore.ending_route = None
                        if isinstance(element, Isolation):
                            isolation : Isolation = element
                            current_isolation = self.get_element_at_grid_pos(train.last_grid_pos)
                            if current_isolation and isinstance(current_isolation, Isolation) and current_isolation != isolation and len(isolation.occuping_trains) > 0:
                                skip_train = True
                                break
                        if not hasattr(element, "movable") or element.movable:
                            break
                        else:
                            offset += 1
                            advance_position = train.get_next_position(dt, offset)
                            grid_pos = get_grid_post(advance_position)
                            element = self.get_element_at_grid_pos(grid_pos)   
                    if skip_train:
                        train.update(self, train.position, dt) 
                        continue      
                else:
                    if train.last_grid_pos:
                        if element := self.get_element_at_grid_pos(train.last_grid_pos):
                            if hasattr(element, "remove_train"):
                                element.remove_train(train) 
                    trains_to_remove.append(train)
                    continue   
            
            for crossing in self.crossings.values():
                if MoveDirection.LEFT in train.move_directions and train.position[0] > crossing.center_x and advance_position[0] < crossing.center_x:
                    crossing.remove_route()
                if MoveDirection.RIGHT in train.move_directions and train.position[0] < crossing.center_x and advance_position[0] > crossing.center_x:
                    crossing.remove_route()
            
            train.update(self, advance_position, dt) 
            if grid_pos != train.last_grid_pos:
                if element := self.get_element_at_grid_pos(train.last_grid_pos):
                    if hasattr(element, "remove_train"):
                        element.remove_train(train) 
                        
            train.last_grid_pos = grid_pos
            train.advance_grid_pos = train.calculate_advance_grid_pos(grid_pos)
            
            if element := self.get_element_at_grid_pos(grid_pos):
                if isinstance(element, Point):
                    train.deduce_move_direction_from_point(element)
                elif isinstance(element, Isolation) and "Vertical" in element.name:
                    train.deduce_move_direction_from_vertical_isolation()
                elif isinstance(element, Isolation) and "Curve" in element.name:
                    train.deduce_move_direction_from_curve(element.name)
                else:
                    train.move_directions = [train.default_direction]
                if hasattr(element, "is_sbl") and element.is_sbl:
                    train.speed_mult = 0.5
                else:
                    train.speed_mult = 1.0
                if hasattr(element, "add_train"):
                    element.add_train(train) 
        for train in trains_to_remove[::-1]:
            self.remove_active_train(train)

    def delay_action(self, delay_seconds: float, action_function: Callable):
        if delay_seconds <= 0:
            action_function()
        else:
            self.pending_tasks.append({
                "timer": delay_seconds,
                "action": action_function,
            })