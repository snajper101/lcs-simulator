from typing import Tuple
from elements.line_blockade import LineBlockade
from elements.isolation import Isolation

class Track():
    def __init__(self, name: str, position_str: str, normal: bool, direction: str, line_block: LineBlockade, isolation: Isolation):
        self.name : str = name
        self.position: Tuple[int, int] = tuple(map(int, position_str.split('-')))
        self.normal: bool = normal
        self.direction: str = direction
        self.line_block = line_block
        self.isolation = isolation
    