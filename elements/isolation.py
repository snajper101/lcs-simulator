from typing import List
from elements.train import Train
class Isolation():
    def __init__(self, name: str, number: str, is_sbl: bool = False) -> str:
        self.name : str = name
        self.number : str = number.split("/")[0]
        self.junctions : List[str] = self.number.replace("Jz", "").split("_")
        self.is_sbl : bool = is_sbl
        
        self.isolation_type : str = len(number.split("/")) == 2 and number.split("/")[1] or "0"
        if not self.isolation_type in ["0", "1", "2", "11", "12", "21", "22", "01", "02", "10", "20", "ab+", "ab-", "cd+", "cd-"]:
            self.isolation_type = "0"
        
        self.route = None
        self.reserved_route = None
        self.is_train_route = True
        self.occuping_trains : List[Train] = []
        
    def route_valid_for_isolation(self, route) -> bool:
        point_id = lambda x: x.replace("+", "").replace("-", "")
        for junction in self.junctions:
            if not junction in [point_id(route_junction).replace("ab", "").replace("cd", "") for route_junction in route.dependencies]:
                return True
            else:
                plus_junctions = [point_id(route_junction) for route_junction in route.dependencies if "+" in route_junction and point_id(route_junction) in self.junctions]
                minus_junctions = [point_id(route_junction) for route_junction in route.dependencies if "-" in route_junction and point_id(route_junction) in self.junctions]
                self_junctions = sorted([route_junction for route_junction in route.dependencies if point_id(route_junction).replace("ab", "").replace("cd", "") in self.junctions], key=point_id)
                if self.isolation_type == "0":
                    return True
                elif self.isolation_type == "1" and len(plus_junctions) > 0:
                    return True
                elif self.isolation_type == "2" and len(minus_junctions) > 0:
                    return True
                elif self.isolation_type == "11" and len(minus_junctions) == 0:
                    return True
                elif self.isolation_type == "22" and len(plus_junctions) == 0:
                    return True
                elif len(self.junctions) > 1 and self.isolation_type == "12" and "+" in self_junctions[0] and "-" in self_junctions[1]:
                    return True
                elif len(self.junctions) > 1 and self.isolation_type == "01" and "+" in self_junctions[1]:
                    return True
                elif len(self.junctions) > 1 and self.isolation_type == "02" and "-" in self_junctions[1]:
                    return True
                elif len(self.junctions) > 1 and self.isolation_type == "21" and "-" in self_junctions[0] and "+" in self_junctions[1]:
                    return True
                elif len(self.junctions) > 1 and self.isolation_type == "10" and "+" in self_junctions[0]:
                    return True
                elif len(self.junctions) > 1 and self.isolation_type == "20" and "-" in self_junctions[0]:
                    return True
                elif f"{junction}{self.isolation_type}" in self_junctions:
                    return True
        return False
        
    def set_route(self, route):
        if not route:
            return
        
        if self.route_valid_for_isolation(route):
            self.route = route
            self.reserved_route = None
            self.is_train_route = route.is_train_route
        
    def remove_route(self):
        self.route = None
        self.reserved_route = None
        
    def reserve_route(self, route):
        if self.route_valid_for_isolation(route):
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