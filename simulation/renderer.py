import pygame
from constants import Constants, MoveDirection
from typing import Dict, Tuple, List
from elements.semaphore import Semaphore, SignalState, SignalType
from elements.point import Point
from simulation.simulator import Simulator
from elements.crossing import Crossing, CrossingState
from elements.line_blockade import LineBlockade, BlocadeDirection
from elements.train_spawner import TrainSpawner
from elements.isolation import Isolation
import math
import time
from datetime import datetime
import interface
import pygame_gui

class GameRenderer:
    def __init__(self):
        self.font_title = pygame.font.SysFont("Arial", 24, bold=True)
        self.font = pygame.font.SysFont("Arial", 12, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 10)
        self.sem_font = pygame.font.SysFont("Arial", 14, bold=True)
        self.destination_font = pygame.font.SysFont("Arial", 8)
  
    def get_coordinates_from_grid(self, coord_str: str) -> Tuple | None:
        try:
            grid_x, grid_y = map(int, coord_str.split('-'))
        except ValueError:
            return None
        
        return (int(self.camera_x + (grid_x * Constants.TILE_SIZE)), int(self.camera_y + (grid_y * Constants.TILE_SIZE)))
    
    def get_coordinates_from_position(self, position: Tuple[int, int]) -> Tuple:
        return (int(self.camera_x + position[0]), int(self.camera_y + position[1])) 
  
    def draw_object_outline(self, grid_pos: str, element: Dict, pressed: bool, rect : pygame.Rect, colour: Tuple[int, int, int], index : int = 0) -> None:
        elem_name = element.get("Name", "")
        if labels := element.get("TextLabels", ""):
            if crossing_id := labels.get("CrossingID"):
                crossing_north = self.simulator.select_crossing_object_by_id("Crossing_North", crossing_id)
                crossing_south = self.simulator.select_crossing_object_by_id("Crossing_South", crossing_id)
                if crossing_north is not None and crossing_south is not None:
                    coord_north = self.get_coordinates_from_grid(crossing_north[0])
                    coord_south = self.get_coordinates_from_grid(crossing_south[0])
                    crossing_rect = pygame.Rect(coord_north[0], coord_north[1], Constants.TILE_SIZE, abs(coord_north[1] - coord_south[1]) + Constants.TILE_SIZE)
                    pygame.draw.rect(self.surface, colour, crossing_rect, 2, 4) 
            elif not "Platform" in elem_name:
                pygame.draw.rect(self.surface, colour, rect, 2, 4) 
        object = self.simulator.logical_elements.get(grid_pos)      
        if pressed and index == 0 and object and isinstance(object, Semaphore):
            number = labels.get("Number", labels.get("Index"))
            if signal_controller := self.simulator.signals.get(number):
                for route in signal_controller.routes:
                    advance_signal : Semaphore = route.advance_signal
                    if advance_signal is not None:
                        coord = self.get_coordinates_from_grid(f"{advance_signal.position[0]}-{advance_signal.position[1]}")
                        pygame.draw.circle(self.surface, colour, (coord[0] + Constants.TILE_SIZE // 2, coord[1] + Constants.TILE_SIZE // 2), Constants.TILE_SIZE * 0.75, 2)

    def should_draw_crossing(self, crossing: Crossing) -> bool:
        if not crossing:
            return False
        if not crossing.changing:
            return True
        else:
            left = time.time() - crossing.change_start_time
            return round(left * 1.5) < left * 1.5
        
    def should_draw_line_block(self, line_block: LineBlockade) -> bool:
        if not line_block:
            return False
        if not line_block.changing:
            return True
        else:
            left = time.time() - line_block.change_start_time
            return round(left * 1.5) < left * 1.5
            
  
    def draw_map(self, surface: pygame.Surface, ui_manager: pygame_gui.UIManager, simulator: Simulator, camera_offset: Tuple[int, int], mouse_pos: Tuple[int, int] = None, pressed_positions : List[str] = None) -> None:
        surface.fill(Constants.BG_COLOR)
        
        self.camera_x, self.camera_y = camera_offset
        self.simulator = simulator
        self.surface = surface
        
        if pressed_positions is None:
            pressed_positions = []

        x_coords = sorted(set(int(x.split("-")[0]) for x in simulator.current_map_data.keys()))

        for coord_str, elements in simulator.current_map_data.items():            
            screen_x, screen_y = self.get_coordinates_from_grid(coord_str)
            grid_x, grid_y = map(int, coord_str.split('-'))
            
            if (screen_x < -Constants.TILE_SIZE or screen_x > surface.get_width() or 
                screen_y < -Constants.TILE_SIZE or screen_y > surface.get_height()):
                continue

            rect = pygame.Rect(screen_x, screen_y, Constants.TILE_SIZE, Constants.TILE_SIZE)
            cx, cy = rect.center
            real_cx, real_cy = rect.center
            
            object = simulator.logical_elements.get(coord_str)
            semaphore, point, crossing, line_block, train_spawner, isolation_ref = None, None, None, None, None, None
            if object and isinstance(object, Semaphore):
                semaphore : Semaphore = object
                if semaphore.signal_type == SignalType.SEMI_AUTO:
                    if semaphore.state == SignalState.S1 or semaphore.state == SignalState.MS1:  
                        sem_colour = (255, 0, 0)
                    else:
                        sem_colour = (0, 255, 0)
                elif semaphore.signal_type == SignalType.REPEATER:
                    if semaphore.advance_signal and semaphore.advance_signal.state == SignalState.S1:
                        sem_colour = "SignalReapeter" in semaphore.name and (255, 0, 0) or (255, 125, 0)
                    elif not semaphore.advance_signal:
                        sem_colour = (255, 0, 0)
                    else:
                        sem_colour = (0, 255, 0)
            elif object and isinstance(object, Point):
                point: Point = object
            elif object and isinstance(object, Crossing):
                crossing: Crossing = object
            elif object and isinstance(object, LineBlockade):
                line_block: LineBlockade = object
            elif object and isinstance(object, TrainSpawner):
                train_spawner: TrainSpawner = object
            elif object and isinstance(object, Isolation):
                isolation_ref: Isolation = object
            else:
                sem_colour = Constants.TRACK_COLOR

            for element in elements:
                elem_name = element.get("Name", "")
                track_color = Constants.TRACK_COLOR
                if isolation_ref:
                    if isolation_ref.route:
                        track_color = isolation_ref.is_train_route and (0, 255, 0) or (255, 255, 0)
                if point and len(point.routes) > 0:
                    track_color = point.routes[0].is_train_route and (0, 255, 0) or (255, 255, 0)
                if hasattr(object, "occuping_trains") and len(object.occuping_trains) > 0:
                    track_color = (255, 0, 0)
                
                if elem_name == "Non_Isolated_Horizontal":
                    pygame.draw.line(surface, track_color, (rect.left, cy), (rect.right, cy), Constants.LINE_ISOLATION_WIDTH)
                elif elem_name == "Isolation_Shortened_Horizontal_Number":
                    start_pos = (rect.left + 4, cy)
                    end_pos = (rect.right - 4, cy)
                    pygame.draw.line(surface, track_color, start_pos, end_pos, Constants.ISOLATION_WIDTH)
                elif "Horizontal" in elem_name and not "Platform" in elem_name:
                    offset = element.get("Offset") or (25, 0)
                    size = element.get("Size") or (50, 0)
                    
                    center_x = rect.left + (offset[0] / 50) * Constants.TILE_SIZE
                    half_width = (size[0] / 50 ) * Constants.TILE_SIZE / 2
                    
                    start_pos = (center_x - half_width, cy)
                    end_pos = (center_x + half_width, cy)
                    real_cx = center_x
                    pygame.draw.line(surface, track_color, start_pos, end_pos, Constants.ISOLATION_WIDTH)
                    rect = pygame.Rect(center_x - half_width, screen_y, 2 * half_width, Constants.TILE_SIZE)
                elif "Vertical" in elem_name:
                    if crossing:
                        if not self.should_draw_crossing(crossing):
                            continue
                        color = crossing.state == CrossingState.OPENED and (255, 153, 255) or Constants.TRACK_COLOR
                    else:
                        color = track_color
                    offset = element.get("Offset") or (0, 25)
                    size = element.get("Size") or (0, 50)
                    
                    center_y = rect.top + (offset[1] / 50) * Constants.TILE_SIZE
                    half_height = (size[1] / 50 ) * Constants.TILE_SIZE / 2
                    
                    start_pos = (cx, center_y - half_height)
                    end_pos = (cx, center_y + half_height)
                    real_cy = center_y
                    pygame.draw.line(surface, color, start_pos, end_pos, Constants.ISOLATION_WIDTH)
                    rect = pygame.Rect(screen_x, center_y - half_height, Constants.TILE_SIZE, 2 * half_height)
                elif "Platform" in elem_name:
                    tileSizeHalf = Constants.TILE_SIZE // 2
                    if "North" in elem_name:
                        start_pos = (rect.left - tileSizeHalf, rect.top)
                        end_pos = (rect.right + tileSizeHalf, rect.top)
                        pygame.draw.line(surface, Constants.TRACK_COLOR, start_pos, end_pos, Constants.LINE_ISOLATION_WIDTH)

                        start_pos_bottom = (rect.left - tileSizeHalf, rect.top + 8)
                        end_pos_bottom = (rect.right + tileSizeHalf, rect.top + 8)
                        pygame.draw.line(surface, Constants.TRACK_COLOR, start_pos_bottom, end_pos_bottom, Constants.LINE_ISOLATION_WIDTH)

                        start_pos_left = (rect.left - tileSizeHalf, rect.top)
                        end_pos_left = (rect.left - tileSizeHalf, rect.bottom + tileSizeHalf - 10)
                        pygame.draw.line(surface, Constants.TRACK_COLOR, start_pos_left, end_pos_left, Constants.LINE_ISOLATION_WIDTH)

                        start_pos_right = (rect.right + tileSizeHalf, rect.top)
                        end_pos_right = (rect.right + tileSizeHalf, rect.bottom + tileSizeHalf - 10)
                        pygame.draw.line(surface, Constants.TRACK_COLOR, start_pos_right, end_pos_right, Constants.LINE_ISOLATION_WIDTH)
                    elif "South" in elem_name:
                        start_pos = (rect.left - tileSizeHalf, rect.bottom)
                        end_pos = (rect.right + tileSizeHalf, rect.bottom)
                        pygame.draw.line(surface, Constants.TRACK_COLOR, start_pos, end_pos, Constants.LINE_ISOLATION_WIDTH)

                        start_pos_bottom = (rect.left - tileSizeHalf, rect.bottom - 8)
                        end_pos_bottom = (rect.right + tileSizeHalf, rect.bottom - 8)
                        pygame.draw.line(surface, Constants.TRACK_COLOR, start_pos_bottom, end_pos_bottom, Constants.LINE_ISOLATION_WIDTH)

                        start_pos_left = (rect.left - tileSizeHalf, rect.bottom)
                        end_pos_left = (rect.left - tileSizeHalf, rect.top - tileSizeHalf + 10)
                        pygame.draw.line(surface, Constants.TRACK_COLOR, start_pos_left, end_pos_left, Constants.LINE_ISOLATION_WIDTH)

                        start_pos_right = (rect.right + tileSizeHalf, rect.bottom)
                        end_pos_right = (rect.right + tileSizeHalf, rect.top - tileSizeHalf + 10)
                        pygame.draw.line(surface, Constants.TRACK_COLOR, start_pos_right, end_pos_right, Constants.LINE_ISOLATION_WIDTH)
                    else:
                        start_pos_left = (rect.left - tileSizeHalf, rect.top)
                        end_pos_left = (rect.left - tileSizeHalf, rect.bottom)
                        pygame.draw.line(surface, Constants.TRACK_COLOR, start_pos_left, end_pos_left, Constants.LINE_ISOLATION_WIDTH)

                        start_pos_right = (rect.right + tileSizeHalf, rect.top)
                        end_pos_right = (rect.right + tileSizeHalf, rect.bottom)
                        pygame.draw.line(surface, Constants.TRACK_COLOR, start_pos_right, end_pos_right, Constants.LINE_ISOLATION_WIDTH)
                        
                        start_pos = (rect.left- tileSizeHalf, rect.top)
                        end_pos = (rect.right + tileSizeHalf, rect.top)
                        pygame.draw.line(surface, Constants.TRACK_COLOR, start_pos, end_pos, Constants.LINE_ISOLATION_WIDTH)
                        
                                                
                        start_pos = (rect.left- tileSizeHalf, rect.top + 5)
                        end_pos = (rect.right + tileSizeHalf, rect.top + 5)
                        pygame.draw.line(surface, Constants.TRACK_COLOR, start_pos, end_pos, Constants.LINE_ISOLATION_WIDTH)

                        start_pos_bottom = (rect.left - tileSizeHalf, rect.bottom)
                        end_pos_bottom = (rect.right + tileSizeHalf, rect.bottom)
                        pygame.draw.line(surface, Constants.TRACK_COLOR, start_pos_bottom, end_pos_bottom, Constants.LINE_ISOLATION_WIDTH)
                        
                        start_pos_bottom = (rect.left - tileSizeHalf, rect.bottom - 5)
                        end_pos_bottom = (rect.right + tileSizeHalf, rect.bottom - 5 )
                        pygame.draw.line(surface, Constants.TRACK_COLOR, start_pos_bottom, end_pos_bottom, Constants.LINE_ISOLATION_WIDTH)
                elif "LineBlockNew" == elem_name:
                    tileSizeHalf = Constants.TILE_SIZE // 2
                    state = line_block.changing and line_block.target_state or line_block.state
                    if state == BlocadeDirection.IDLE:
                        arrow_color = Constants.TRACK_COLOR
                    else:
                        arrow_color = (255, 255, 0)
                    if state == BlocadeDirection.IDLE or state == BlocadeDirection.RIGHT:
                        traingle_left = [(cx + tileSizeHalf - 8, cy - tileSizeHalf + 8), 
                            (cx + tileSizeHalf - 8, cy + tileSizeHalf - 8), 
                            (rect.right, cy)]
                        pygame.draw.polygon(surface, arrow_color, traingle_left)
                    if state == BlocadeDirection.IDLE or state == BlocadeDirection.LEFT:
                        triangle_right = [(cx - tileSizeHalf + 8, cy - tileSizeHalf + 8), 
                            (cx - tileSizeHalf + 8, cy + tileSizeHalf - 8), 
                            (rect.left, cy)]
                        pygame.draw.polygon(surface, arrow_color, triangle_right)
                    if not line_block.changing:
                        if state == BlocadeDirection.IDLE or state == BlocadeDirection.RIGHT:
                            start_pos_left = (rect.left, rect.top - 2)
                            end_pos_left = (cx - tileSizeHalf + 8, rect.top - 2)
                            pygame.draw.line(surface, state == BlocadeDirection.IDLE and Constants.TRACK_COLOR or (0, 255, 0), start_pos_left, end_pos_left, 4)
                        if state == BlocadeDirection.IDLE or state == BlocadeDirection.LEFT:
                            start_pos_right = (rect.right, rect.top - 2)
                            end_pos_right = (cx + tileSizeHalf - 8, rect.top - 2)
                            pygame.draw.line(surface, state == BlocadeDirection.IDLE and Constants.TRACK_COLOR or (0, 255, 0), start_pos_right, end_pos_right, 4)
                    if self.should_draw_line_block(line_block):        
                        if state == BlocadeDirection.IDLE:      
                            start_center = (cx - tileSizeHalf + 12, cy)
                            end_center = (cx + tileSizeHalf - 12, cy)
                        elif state == BlocadeDirection.LEFT:
                            start_center = (cx - tileSizeHalf + 12, cy)
                            end_center = (rect.right - 4, cy)
                        else:
                            start_center = (cx + tileSizeHalf - 12, cy)
                            end_center = (rect.left + 4, cy)
                        pygame.draw.line(surface, arrow_color, start_center, end_center, 10)
                elif "Point" in elem_name and not point.changing:
                    if point.direction == "+":
                        pygame.draw.line(surface, track_color, (rect.left, cy), (rect.right, cy), Constants.ISOLATION_WIDTH)
                    else:
                        if "South_West" in elem_name:
                            horizontal_start = (rect.left, cy)
                            horizontal_end = (rect.left + 4, cy)
                            pygame.draw.line(surface, track_color, horizontal_start, horizontal_end, Constants.ISOLATION_WIDTH)
                            vertical_start = (cx, rect.bottom - 4)
                            vertical_end = (cx, rect.bottom)
                            pygame.draw.line(surface, track_color, vertical_start, vertical_end, Constants.ISOLATION_WIDTH)
                            curve = [(rect.left + 4, cy + Constants.ISOLATION_WIDTH // 2), 
                                (rect.left + 4, cy - (Constants.ISOLATION_WIDTH - 1 )  // 2),
                                (cx + Constants.ISOLATION_WIDTH // 2, rect.bottom - 4), 
                                (cx - Constants.ISOLATION_WIDTH // 2, rect.bottom - 4),
                            ]
                            pygame.draw.polygon(surface, track_color, curve)
                        elif "South_East" in elem_name:
                            horizontal_start = (rect.right, cy)
                            horizontal_end = (rect.right - 4, cy)
                            pygame.draw.line(surface, track_color, horizontal_start, horizontal_end, Constants.ISOLATION_WIDTH)
                            vertical_start = (cx, rect.bottom - 4)
                            vertical_end = (cx, rect.bottom)
                            pygame.draw.line(surface, track_color, vertical_start, vertical_end, Constants.ISOLATION_WIDTH)
                            curve = [(rect.right - 4, cy + Constants.ISOLATION_WIDTH // 2), 
                                (rect.right - 4, cy - (Constants.ISOLATION_WIDTH - 1 ) // 2),
                                (cx - (Constants.ISOLATION_WIDTH - 1 ) // 2, rect.bottom - 4),
                                (cx + Constants.ISOLATION_WIDTH // 2, rect.bottom - 4), 
                            ]
                            pygame.draw.polygon(surface, track_color, curve)      
                        elif "North_East" in elem_name:
                            horizontal_start = (rect.right, cy)
                            horizontal_end = (rect.right - 4, cy)
                            pygame.draw.line(surface, track_color, horizontal_start, horizontal_end, Constants.ISOLATION_WIDTH)
                            vertical_start = (cx, rect.top + 4)
                            vertical_end = (cx, rect.top)
                            pygame.draw.line(surface, track_color, vertical_start, vertical_end, Constants.ISOLATION_WIDTH)
                            curve = [(rect.right - 4, cy + Constants.ISOLATION_WIDTH // 2), 
                                (rect.right - 4, cy - (Constants.ISOLATION_WIDTH - 1 ) // 2),
                                (cx + Constants.ISOLATION_WIDTH // 2, rect.top + 4), 
                                (cx - (Constants.ISOLATION_WIDTH - 1 ) // 2, rect.top + 4),
                            ]
                            pygame.draw.polygon(surface, track_color, curve) 
                        else:
                            horizontal_start = (rect.left, cy)
                            horizontal_end = (rect.left + 4, cy)
                            pygame.draw.line(surface, track_color, horizontal_start, horizontal_end, Constants.ISOLATION_WIDTH)
                            vertical_start = (cx, rect.top + 4)
                            vertical_end = (cx, rect.top)
                            pygame.draw.line(surface, track_color, vertical_start, vertical_end, Constants.ISOLATION_WIDTH)
                            curve = [(rect.left + 4, cy + Constants.ISOLATION_WIDTH // 2), 
                                (rect.left + 4, cy - (Constants.ISOLATION_WIDTH - 1 ) // 2),
                                (cx - (Constants.ISOLATION_WIDTH - 1 ) // 2, rect.top + 4),
                                (cx + Constants.ISOLATION_WIDTH // 2, rect.top + 4), 
                            ]
                            pygame.draw.polygon(surface, track_color, curve)
                elif "SemOnlyShunt" in elem_name:
                    if "East" in elem_name:
                        points_top = [(rect.left + 10, rect.top + 4), 
                            (rect.left + 14, rect.top + 4), 
                            (cx + 10, cy),
                            (cx + 6, cy),
                        ]
                        points_bottom = [(cx + 10, cy),
                            (cx + 6, cy),                      
                            (rect.left + 10, rect.bottom - 4),
                            (rect.left + 14, rect.bottom - 4)
                        ]
                        pygame.draw.polygon(surface, sem_colour, points_top)
                        pygame.draw.polygon(surface, sem_colour, points_bottom)
                    else:
                        points_top = [(rect.right - 10, rect.top + 4), 
                            (rect.right - 14, rect.top + 4), 
                            (cx - 10, cy),
                            (cx - 6, cy),
                        ]
                        points_bottom = [(cx - 10, cy),
                            (cx - 6, cy),                      
                            (rect.right - 10, rect.bottom - 4),
                            (rect.right - 14, rect.bottom - 4)
                        ]
                        pygame.draw.polygon(surface, sem_colour, points_top)
                        pygame.draw.polygon(surface, sem_colour, points_bottom)
                elif "TrainShunt" in elem_name:
                    tileSizeHalf = Constants.TILE_SIZE // 2
                    if "East" in elem_name:
                        points_top = [(rect.left + 4, rect.top + 4), 
                            (rect.left + 8, rect.top + 4), 
                            (cx + 4, cy),
                            (cx, cy)
                        ]
                        points_bottom = [(cx + 4, cy),
                            (cx, cy),                      
                            (rect.left + 4, rect.bottom - 4),
                            (rect.left + 8, rect.bottom - 4)
                        ]
                        pygame.draw.polygon(surface, sem_colour, points_top)
                        pygame.draw.polygon(surface, sem_colour, points_bottom)
                        points = [(rect.right - 16, rect.top + 4), 
                            (rect.right - 16, rect.bottom - 4), 
                            (rect.right - 4, cy)]
                        pygame.draw.polygon(surface, sem_colour, points)
                    else:
                        points_top = [(rect.right - 4, rect.top + 4), 
                            (rect.right - 8, rect.top + 4), 
                            (cx - 4, cy),
                            (cx, cy),
                        ]
                        points_bottom = [(cx - 4, cy),
                            (cx, cy),                      
                            (rect.right - 4, rect.bottom - 4),
                            (rect.right - 8, rect.bottom - 4)
                        ]
                        pygame.draw.polygon(surface, sem_colour, points_top)
                        pygame.draw.polygon(surface, sem_colour, points_bottom)
                        points = [(rect.left + 16, rect.top + 4), 
                            (rect.left + 16, rect.bottom - 4), 
                            (rect.left + 4, cy)]
                        pygame.draw.polygon(surface, sem_colour, points)
                elif "Sem" in elem_name:
                    tileSizeHalf = Constants.TILE_SIZE // 2
                    if "West" in elem_name:
                        points = [(cx + tileSizeHalf - 8, cy - tileSizeHalf + 8), 
                            (cx + tileSizeHalf - 8, cy + tileSizeHalf - 8), 
                            (cx - tileSizeHalf + 8, cy)]
                        pygame.draw.polygon(surface, sem_colour, points)
                    elif "East" in elem_name:
                        points = [(cx - tileSizeHalf + 8, cy - tileSizeHalf + 8), 
                            (cx - tileSizeHalf + 8, cy + tileSizeHalf - 8), 
                            (cx + tileSizeHalf - 8, cy)]
                        pygame.draw.polygon(surface, sem_colour, points)
                elif "To_" in elem_name:
                    if "East" in elem_name:
                        points_top = [(rect.left + 10, rect.top + 4), 
                            (rect.left + 14, rect.top + 4), 
                            (cx + 10, cy),
                            (cx + 6, cy),
                        ]
                        points_bottom = [(cx + 10, cy),
                            (cx + 6, cy),                      
                            (rect.left + 10, rect.bottom - 4),
                            (rect.left + 14, rect.bottom - 4)
                        ]
                        pygame.draw.polygon(surface, sem_colour, points_top)
                        pygame.draw.polygon(surface, sem_colour, points_bottom)
                        pygame.draw.circle(surface, sem_colour, (cx - 2, cy), 3)
                    else:
                        points_top = [(rect.right - 10, rect.top + 4), 
                            (rect.right - 14, rect.top + 4), 
                            (cx - 10, cy),
                            (cx - 6, cy),
                        ]
                        points_bottom = [(cx - 10, cy),
                            (cx - 6, cy),                      
                            (rect.right - 10, rect.bottom - 4),
                            (rect.right - 14, rect.bottom - 4)
                        ]
                        pygame.draw.polygon(surface, sem_colour, points_top)
                        pygame.draw.polygon(surface, sem_colour, points_bottom)
                        pygame.draw.circle(surface, sem_colour, (cx + 2, cy), 3)
                elif "TrackEnd_" in elem_name:
                    if "West" in elem_name:
                        pygame.draw.line(surface, Constants.TRACK_COLOR, (cx, cy), (rect.left, cy), Constants.ISOLATION_WIDTH)
                        pygame.draw.line(surface, Constants.TRACK_COLOR, (cx + 1, rect.bottom - 2), (cx + 1, rect.top + 2), 2) # Vertical
                        pygame.draw.line(surface, Constants.TRACK_COLOR, (cx + 1, rect.bottom - 2), (rect.left + 2, rect.bottom - 2), 2) #HorizontalBottom
                        pygame.draw.line(surface, Constants.TRACK_COLOR, (cx + 1, rect.top + 2), (rect.left + 2, rect.top + 2), 2) #HorizontalTop
                    else:
                        pygame.draw.line(surface, Constants.TRACK_COLOR, (cx, cy), (rect.right, cy), Constants.ISOLATION_WIDTH)
                        pygame.draw.line(surface, Constants.TRACK_COLOR, (cx - 1, rect.bottom - 2), (cx - 1, rect.top + 2), 2) # Vertical
                        pygame.draw.line(surface, Constants.TRACK_COLOR, (cx - 1, rect.bottom - 2), (rect.right - 2, rect.bottom - 2), 2) #HorizontalBottom
                        pygame.draw.line(surface, Constants.TRACK_COLOR, (cx - 1, rect.top + 2), (rect.right - 2, rect.top + 2), 2) #HorizontalTop
                elif "Derailer_North" in elem_name:
                    if "North" in elem_name:
                        pygame.draw.line(surface, Constants.TRACK_COLOR, (rect.left, cy), (rect.left + 6, cy), Constants.ISOLATION_WIDTH)
                        pygame.draw.line(surface, Constants.TRACK_COLOR, (cx, cy - 8), (cx, cy + 8), Constants.LINE_ISOLATION_WIDTH)
                        pygame.draw.line(surface, Constants.TRACK_COLOR, (rect.right, cy), (rect.right - 6, cy), Constants.ISOLATION_WIDTH)
                elif "Crossing_" in elem_name and crossing:
                    if not self.should_draw_crossing(crossing):
                        continue
                    crossing_colour = crossing.state == CrossingState.OPENED and (255, 153, 255) or (crossing.route_count > 0 and (255, 255, 0) or Constants.TRACK_COLOR)
                    tileSizeHalf = Constants.TILE_SIZE // 2
                    if "North" in elem_name:
                        points_left = [(rect.left + 2, rect.top + 4), 
                            (rect.left + 6, rect.top + 4),
                            (cx + 2, cy), 
                            (cx - 2, cy),
                        ]
                        points_right = [(cx - 2, cy),
                            (cx + 2, cy),                      
                            (rect.right - 2, rect.top + 4),
                            (rect.right - 6, rect.top + 4)
                        ]
                        start_pos = (cx, cy)
                        end_pos = (cx, cy + tileSizeHalf)
                        pygame.draw.line(surface, crossing_colour, start_pos, end_pos, 3)
                        pygame.draw.polygon(surface, crossing_colour, points_left)
                        pygame.draw.polygon(surface, crossing_colour, points_right)
                    if "South" in elem_name:
                        points_left = [(rect.left + 2, rect.bottom - 4), 
                            (rect.left + 6, rect.bottom - 4),
                            (cx + 2, cy), 
                            (cx - 2, cy),
                        ]
                        points_right = [(cx - 2, cy),
                            (cx + 2, cy),                      
                            (rect.right - 2, rect.bottom - 4),
                            (rect.right - 6, rect.bottom - 4)
                        ]
                        start_pos = (cx, cy)
                        end_pos = (cx, cy - tileSizeHalf)
                        pygame.draw.line(surface, crossing_colour, start_pos, end_pos, 3)
                        pygame.draw.polygon(surface, crossing_colour, points_left)
                        pygame.draw.polygon(surface, crossing_colour, points_right)
                elif "Curve_" in elem_name:
                    if "West" in elem_name:
                        horizontal_start = (rect.left, cy)
                        horizontal_end = (rect.left + 4, cy)
                        pygame.draw.line(surface, track_color, horizontal_start, horizontal_end, Constants.ISOLATION_WIDTH)
                        vertical_start = (cx, rect.bottom - 4)
                        vertical_end = (cx, rect.bottom)
                        pygame.draw.line(surface, track_color, vertical_start, vertical_end, Constants.ISOLATION_WIDTH)
                        curve = [(rect.left + 4, cy + Constants.ISOLATION_WIDTH // 2), 
                            (rect.left + 4, cy - (Constants.ISOLATION_WIDTH - 1 )  // 2),
                            (cx + Constants.ISOLATION_WIDTH // 2, rect.bottom - 4), 
                            (cx - Constants.ISOLATION_WIDTH // 2, rect.bottom - 4),
                        ]
                        pygame.draw.polygon(surface, track_color, curve)
                    elif "South" in elem_name:
                        horizontal_start = (rect.right, cy)
                        horizontal_end = (rect.right - 4, cy)
                        pygame.draw.line(surface, track_color, horizontal_start, horizontal_end, Constants.ISOLATION_WIDTH)
                        vertical_start = (cx, rect.bottom - 4)
                        vertical_end = (cx, rect.bottom)
                        pygame.draw.line(surface, track_color, vertical_start, vertical_end, Constants.ISOLATION_WIDTH)
                        curve = [(rect.right - 4, cy + Constants.ISOLATION_WIDTH // 2), 
                            (rect.right - 4, cy - (Constants.ISOLATION_WIDTH - 1 ) // 2),
                            (cx - (Constants.ISOLATION_WIDTH - 1 ) // 2, rect.bottom - 4),
                            (cx + Constants.ISOLATION_WIDTH // 2, rect.bottom - 4), 
                        ]
                        pygame.draw.polygon(surface, track_color, curve)      
                    elif "East" in elem_name:
                        horizontal_start = (rect.right, cy)
                        horizontal_end = (rect.right - 4, cy)
                        pygame.draw.line(surface, track_color, horizontal_start, horizontal_end, Constants.ISOLATION_WIDTH)
                        vertical_start = (cx, rect.top + 4)
                        vertical_end = (cx, rect.top)
                        pygame.draw.line(surface, track_color, vertical_start, vertical_end, Constants.ISOLATION_WIDTH)
                        curve = [(rect.right - 4, cy + Constants.ISOLATION_WIDTH // 2), 
                            (rect.right - 4, cy - (Constants.ISOLATION_WIDTH - 1 ) // 2),
                            (cx + Constants.ISOLATION_WIDTH // 2, rect.top + 4), 
                            (cx - (Constants.ISOLATION_WIDTH - 1 ) // 2, rect.top + 4),
                        ]
                        pygame.draw.polygon(surface, track_color, curve) 
                    else:
                        horizontal_start = (rect.left, cy)
                        horizontal_end = (rect.left + 4, cy)
                        pygame.draw.line(surface, track_color, horizontal_start, horizontal_end, Constants.ISOLATION_WIDTH)
                        vertical_start = (cx, rect.top + 4)
                        vertical_end = (cx, rect.top)
                        pygame.draw.line(surface, track_color, vertical_start, vertical_end, Constants.ISOLATION_WIDTH)
                        curve = [(rect.left + 4, cy + Constants.ISOLATION_WIDTH // 2), 
                            (rect.left + 4, cy - (Constants.ISOLATION_WIDTH - 1 ) // 2),
                            (cx - (Constants.ISOLATION_WIDTH - 1 ) // 2, rect.top + 4),
                            (cx + Constants.ISOLATION_WIDTH // 2, rect.top + 4), 
                        ]
                        pygame.draw.polygon(surface, track_color, curve)
                elif "TrainEnd_" in elem_name:
                    if semaphore and semaphore.ending_route:
                        color = (255, 0, 0)
                    else:
                        color = (255, 255, 255)
                    if "West" in elem_name:
                        points = [(cx + tileSizeHalf - 10, cy - tileSizeHalf + 10), 
                            (cx + tileSizeHalf - 10, cy + tileSizeHalf - 10), 
                            (cx - tileSizeHalf + 10, cy)]
                        pygame.draw.polygon(surface, color, points)
                    elif "East" in elem_name:
                        points = [(cx - tileSizeHalf + 10, cy - tileSizeHalf + 10), 
                            (cx - tileSizeHalf + 10, cy + tileSizeHalf - 10), 
                            (cx + tileSizeHalf - 10, cy)]
                        pygame.draw.polygon(surface, color, points)
                elif "ShuntEnd" in elem_name:
                    radius = 10 
                    arc_rect = pygame.Rect(cx - radius, cy - radius - 10, radius * 2, radius * 2)
                    pygame.draw.arc(surface, Constants.TRACK_COLOR, arc_rect, 0, math.pi, 2)
                    pygame.draw.line(surface, Constants.TRACK_COLOR, (cx - radius, cy - 10), (cx + radius, cy -10), 2)
                elif "SignalReapeter" in elem_name:
                    tileSizeHalf = Constants.TILE_SIZE // 2
                    if "West" in elem_name:
                        points = [(cx + tileSizeHalf - 8, cy - tileSizeHalf + 8), 
                            (cx + tileSizeHalf - 8, cy + tileSizeHalf - 8), 
                            (cx - tileSizeHalf + 8, cy)]
                        pygame.draw.polygon(surface, sem_colour, points, 2)
                    elif "East" in elem_name:
                        points = [(cx - tileSizeHalf + 8, cy - tileSizeHalf + 8), 
                            (cx - tileSizeHalf + 8, cy + tileSizeHalf - 8), 
                            (cx + tileSizeHalf - 8, cy)]
                        pygame.draw.polygon(surface, sem_colour, points, 2)
                if "TextLabels" in element:
                    labels = element["TextLabels"]
                    label_text = labels.get("Number", labels.get("Index", labels.get("IsolationName", labels.get("StationName", labels.get("Destination")))))
                    direction = "" if point is None else point.direction
                    if label_text:
                        if "StationName" in labels:
                            text_surf = self.font_title.render(label_text, True, Constants.TRACK_COLOR)
                            text_rect = text_surf.get_rect(center=(cx, cy))
                            surface.blit(text_surf, text_rect)
                            clock_text_surf = self.font_title.render(datetime.now().strftime("%H:%M:%S"), True, Constants.TRACK_COLOR)
                            clock_text_rect = clock_text_surf.get_rect(center=(cx, cy - 30))
                            surface.blit(clock_text_surf, clock_text_rect)
                        elif "LineTrainSpawner" in elem_name and train_spawner:
                            text = f"{label_text} {len(train_spawner.waiting_trains)}"
                            color = Constants.TRACK_COLOR
                            if train_spawner.delayed:
                                color = (255, 125, 0)
                            elif len(train_spawner.waiting_trains) > 0:
                                color = (255,255,255)
                            x_size, y_size = self.font.size(text)
                            text_surf = self.font.render(text, True, color)
                            if abs(grid_x - x_coords[0]) < abs(grid_x - x_coords[-1]):
                                text_rect = text_surf.get_rect(center=(rect.left + x_size // 2, cy))
                            else:
                                text_rect = text_surf.get_rect(center=(rect.right - x_size // 2, cy))
                            surface.blit(text_surf, text_rect)
                            text_rect.height = Constants.TILE_SIZE
                            text_rect.centery = cy      
                            rect = train_spawner.hit_box = text_rect
                        elif "Isolation_Shortened_Horizontal_Number" == elem_name:
                            text_surf = self.small_font.render(label_text, True, track_color)
                            text_rect = text_surf.get_rect(center=(cx, cy - 10))
                            surface.blit(text_surf, text_rect)
                        elif "Sem" in elem_name or "To_" in elem_name or "ShuntEnd" in elem_name:
                            color = ( "OnlyShunt" in elem_name or "ShuntEnd" in elem_name ) and (0, 255, 255) or (255, 255, 0)
                            text_surf = self.sem_font.render(label_text, True, color)
                            text_rect = text_surf.get_rect(center=(cx, cy + 18))
                            surface.blit(text_surf, text_rect)
                        elif "SignalReapeter" in elem_name:
                            text_surf = self.sem_font.render(label_text, True, Constants.TRACK_COLOR)
                            text_rect = text_surf.get_rect(center=(cx, cy + 18))
                            surface.blit(text_surf, text_rect)
                        elif "Platform" in elem_name:
                            sign = "South" in elem_name and -1 or 1
                            text_surf = self.font.render(label_text, True, Constants.TRACK_COLOR)
                            text_rect = text_surf.get_rect(center=(cx, cy + sign * ("Horizontal" in elem_name and -1 or 5)))
                            surface.blit(text_surf, text_rect)
                        elif "LineBlockNew" == elem_name:
                            text_surf = self.sem_font.render(label_text, True, (255, 255, 0))
                            text_rect = text_surf.get_rect(center=(cx, rect.top - 10))
                            surface.blit(text_surf, text_rect)
                        elif "Point_South" in elem_name:
                            text_surf = self.small_font.render(f"{label_text} {direction}", True, track_color)
                            text_rect = text_surf.get_rect(center=(cx, cy - 10))
                            surface.blit(text_surf, text_rect)
                        elif "Point_North" in elem_name:
                            text_surf = self.small_font.render(f"{label_text} {direction}", True, track_color)
                            text_rect = text_surf.get_rect(center=(cx, cy + 10))
                            surface.blit(text_surf, text_rect)
                        elif "Crossing_North" == elem_name:
                            text_surf = self.small_font.render(label_text, True, Constants.TRACK_COLOR)
                            text_rect = text_surf.get_rect(center=(cx, cy - 20))
                            surface.blit(text_surf, text_rect)
                        elif "Crossing_South" == elem_name:
                            text_surf = self.small_font.render(label_text, True, Constants.TRACK_COLOR)
                            text_rect = text_surf.get_rect(center=(cx, cy + 20))
                            surface.blit(text_surf, text_rect)
                        elif "Derailer_North" == elem_name:
                            text_surf = self.sem_font.render(label_text, True, (255,255,255))
                            text_rect = text_surf.get_rect(center=(cx, cy - 18))
                            surface.blit(text_surf, text_rect)
                        elif number_text := labels.get("NumberText", ""):
                            text_surf = self.small_font.render(str(number_text), True, Constants.TRACK_COLOR)
                            text_rect = text_surf.get_rect(center=(real_cx, cy))
                            bg_rect = pygame.Rect( text_rect.left - 6, text_rect.top - 4, text_rect.width + 6 * 2, text_rect.height + 4 * 2 )
                            pygame.draw.rect(surface, (0, 0, 0), bg_rect)            
                            surface.blit(text_surf, text_rect)

            pressed = False
            for pressed_coord_str in pressed_positions:
                pressed_coord = self.get_coordinates_from_grid(pressed_coord_str)
                if pressed_coord and rect.collidepoint(pressed_coord):
                    pressed = True
                    self.draw_object_outline(pressed_coord_str, elements[0], True, rect, (0, 255, 255), pressed_positions.index(pressed_coord_str))
                    break
            if not pressed and mouse_pos and rect.collidepoint(mouse_pos):
                if not "Platform" in elements[0].get("Name", ""):
                    self.draw_object_outline(coord_str, elements[0], False, rect, (255, 255, 0))
        
        for train in self.simulator.active_trains:
            position = self.get_coordinates_from_position(train.position)
            rect = train.train_icon.get_rect(center=position)
            surface.blit(train.train_icon, rect)
            text_surf = self.destination_font.render(train.destination, True, (255,255,255))
            text_rect = text_surf.get_rect(center=(position[0], position[1] + 16))
            surface.blit(text_surf, text_rect)
            
        text = f"Punkty: {simulator.user_points}"
        points_text_surf = self.font.render(text, True, (255,255,255))
        points_text_rect = points_text_surf.get_rect(center=(surface.get_width() - self.font.size(text)[0] // 2 - 10, 20))
        surface.blit(points_text_surf, points_text_rect)