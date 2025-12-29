import pygame
from constants import Constants
from typing import Dict, Tuple
from elements.semaphore import Semaphore, SignalState, SignalType
import math

class GameRenderer:
    def __init__(self):
        self.font_title = pygame.font.SysFont("Arial", 24, bold=True)
        self.font = pygame.font.SysFont("Arial", 12, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 10)
        self.sem_font = pygame.font.SysFont("Arial", 14, bold=True)
        
    def draw_map(self, surface: pygame.Surface, map_data: Dict, logical_elements: Dict, camera_offset: Tuple, mouse_pos: Tuple = None, pressed_pos : Tuple = None) -> None:
        surface.fill(Constants.BG_COLOR)
        
        cam_x, cam_y = camera_offset

        for coord_str, elements in map_data.items():
            try:
                grid_x, grid_y = map(int, coord_str.split('-'))
            except ValueError:
                continue
            
            screen_x = int(cam_x + (grid_x * Constants.TILE_SIZE))
            screen_y = int(cam_y + (grid_y * Constants.TILE_SIZE))
            
            if (screen_x < -Constants.TILE_SIZE or screen_x > surface.get_width() or 
                screen_y < -Constants.TILE_SIZE or screen_y > surface.get_height()):
                continue

            rect = pygame.Rect(screen_x, screen_y, Constants.TILE_SIZE, Constants.TILE_SIZE)
            cx, cy = rect.center
            real_cx, real_cy = rect.center
            
            object = logical_elements.get(coord_str)
            if object and isinstance(object, Semaphore):
                semaphore : Semaphore = object
                if semaphore.signal_type == SignalType.SEMI_AUTO:
                    if semaphore.state == SignalState.S1:  
                        sem_colour = (255, 0, 0)
                    else:
                        sem_colour = (0, 255, 0)
                elif semaphore.signal_type == SignalType.REPEATER:
                    if semaphore.advance_signal and semaphore.advance_signal.state == SignalState.S1:
                        sem_colour = (255, 125, 0)
                    else:
                        sem_colour = (0, 255, 0)
            else:
                sem_colour = Constants.TRACK_COLOR

            for element in elements:
                elem_name = element.get("Name", "")
                if elem_name == "Non_Isolated_Horizontal":
                    pygame.draw.line(surface, Constants.TRACK_COLOR, (rect.left, cy), (rect.right, cy), Constants.LINE_ISOLATION_WIDTH)
                elif elem_name == "Isolation_Shortened_Horizontal_Number":
                    start_pos = (rect.left + 4, cy)
                    end_pos = (rect.right - 4, cy)
                    pygame.draw.line(surface, Constants.TRACK_COLOR, start_pos, end_pos, Constants.ISOLATION_WIDTH)
                elif "Horizontal" in elem_name and not "Platform" in elem_name:
                    offset = element.get("Offset") or (25, 0)
                    size = element.get("Size") or (50, 0)
                    
                    center_x = rect.left + (offset[0] / 50) * Constants.TILE_SIZE
                    half_width = (size[0] / 50 ) * Constants.TILE_SIZE / 2
                    
                    start_pos = (center_x - half_width, cy)
                    end_pos = (center_x + half_width, cy)
                    real_cx = center_x
                    pygame.draw.line(surface, Constants.TRACK_COLOR, start_pos, end_pos, Constants.ISOLATION_WIDTH)
                    rect = pygame.Rect(center_x - half_width, screen_y, 2 * half_width, Constants.TILE_SIZE)
                elif "Vertical" in elem_name:
                    offset = element.get("Offset") or (0, 25)
                    size = element.get("Size") or (0, 50)
                    
                    center_y = rect.top + (offset[1] / 50) * Constants.TILE_SIZE
                    half_height = (size[1] / 50 ) * Constants.TILE_SIZE / 2
                    
                    start_pos = (cx, center_y - half_height)
                    end_pos = (cx, center_y + half_height)
                    real_cy = center_y
                    pygame.draw.line(surface, Constants.TRACK_COLOR, start_pos, end_pos, Constants.ISOLATION_WIDTH)
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
                    traingle_left = [(cx + tileSizeHalf - 8, cy - tileSizeHalf + 8), 
                        (cx + tileSizeHalf - 8, cy + tileSizeHalf - 8), 
                        (rect.right, cy)]
                    pygame.draw.polygon(surface, Constants.TRACK_COLOR, traingle_left)
                    triangle_right = [(cx - tileSizeHalf + 8, cy - tileSizeHalf + 8), 
                        (cx - tileSizeHalf + 8, cy + tileSizeHalf - 8), 
                        (rect.left, cy)]
                    pygame.draw.polygon(surface, Constants.TRACK_COLOR, triangle_right)
                    start_pos_left = (rect.left, rect.top - 2)
                    end_pos_left = (cx - tileSizeHalf + 8, rect.top - 2)
                    pygame.draw.line(surface, Constants.TRACK_COLOR, start_pos_left, end_pos_left, 4)
                    start_pos_right = (rect.right, rect.top - 2)
                    end_pos_right = (cx + tileSizeHalf - 8, rect.top - 2)
                    pygame.draw.line(surface, Constants.TRACK_COLOR, start_pos_right, end_pos_right, 4)
                    start_center_right = (cx - tileSizeHalf + 12, cy)
                    end_center_right = (cx + tileSizeHalf - 12, cy)
                    pygame.draw.line(surface, Constants.TRACK_COLOR, start_center_right, end_center_right, 12)
                elif "Point" in elem_name:
                    pygame.draw.line(surface, Constants.TRACK_COLOR, (rect.left, cy), (rect.right, cy), Constants.ISOLATION_WIDTH)
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
                elif "Crossing_" in elem_name:
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
                        pygame.draw.line(surface, Constants.TRACK_COLOR, start_pos, end_pos, 3)
                        pygame.draw.polygon(surface, Constants.TRACK_COLOR, points_left)
                        pygame.draw.polygon(surface, Constants.TRACK_COLOR, points_right)
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
                        pygame.draw.line(surface, Constants.TRACK_COLOR, start_pos, end_pos, 3)
                        pygame.draw.polygon(surface, Constants.TRACK_COLOR, points_left)
                        pygame.draw.polygon(surface, Constants.TRACK_COLOR, points_right)
                elif "Curve_" in elem_name:
                    if "West" in elem_name:
                        horizontal_start = (rect.left, cy)
                        horizontal_end = (rect.left + 4, cy)
                        pygame.draw.line(surface, Constants.TRACK_COLOR, horizontal_start, horizontal_end, Constants.ISOLATION_WIDTH)
                        vertical_start = (cx, rect.bottom - 4)
                        vertical_end = (cx, rect.bottom)
                        pygame.draw.line(surface, Constants.TRACK_COLOR, vertical_start, vertical_end, Constants.ISOLATION_WIDTH)
                        curve = [(rect.left + 4, cy + Constants.ISOLATION_WIDTH // 2), 
                            (rect.left + 4, cy - (Constants.ISOLATION_WIDTH - 1 )  // 2),
                            (cx + Constants.ISOLATION_WIDTH // 2, rect.bottom - 4), 
                            (cx - Constants.ISOLATION_WIDTH // 2, rect.bottom - 4),
                        ]
                        pygame.draw.polygon(surface, Constants.TRACK_COLOR, curve)
                    elif "South" in elem_name:
                        horizontal_start = (rect.right, cy)
                        horizontal_end = (rect.right - 4, cy)
                        pygame.draw.line(surface, Constants.TRACK_COLOR, horizontal_start, horizontal_end, Constants.ISOLATION_WIDTH)
                        vertical_start = (cx, rect.bottom - 4)
                        vertical_end = (cx, rect.bottom)
                        pygame.draw.line(surface, Constants.TRACK_COLOR, vertical_start, vertical_end, Constants.ISOLATION_WIDTH)
                        curve = [(rect.right - 4, cy + Constants.ISOLATION_WIDTH // 2), 
                            (rect.right - 4, cy - (Constants.ISOLATION_WIDTH - 1 ) // 2),
                            (cx - (Constants.ISOLATION_WIDTH - 1 ) // 2, rect.bottom - 4),
                            (cx + Constants.ISOLATION_WIDTH // 2, rect.bottom - 4), 
                        ]
                        pygame.draw.polygon(surface, Constants.TRACK_COLOR, curve)      
                    elif "East" in elem_name:
                        horizontal_start = (rect.right, cy)
                        horizontal_end = (rect.right - 4, cy)
                        pygame.draw.line(surface, Constants.TRACK_COLOR, horizontal_start, horizontal_end, Constants.ISOLATION_WIDTH)
                        vertical_start = (cx, rect.top + 4)
                        vertical_end = (cx, rect.top)
                        pygame.draw.line(surface, Constants.TRACK_COLOR, vertical_start, vertical_end, Constants.ISOLATION_WIDTH)
                        curve = [(rect.right - 4, cy + Constants.ISOLATION_WIDTH // 2), 
                            (rect.right - 4, cy - (Constants.ISOLATION_WIDTH - 1 ) // 2),
                            (cx + Constants.ISOLATION_WIDTH // 2, rect.top + 4), 
                            (cx - (Constants.ISOLATION_WIDTH - 1 ) // 2, rect.top + 4),
                        ]
                        pygame.draw.polygon(surface, Constants.TRACK_COLOR, curve) 
                    else:
                        horizontal_start = (rect.left, cy)
                        horizontal_end = (rect.left + 4, cy)
                        pygame.draw.line(surface, Constants.TRACK_COLOR, horizontal_start, horizontal_end, Constants.ISOLATION_WIDTH)
                        vertical_start = (cx, rect.top + 4)
                        vertical_end = (cx, rect.top)
                        pygame.draw.line(surface, Constants.TRACK_COLOR, vertical_start, vertical_end, Constants.ISOLATION_WIDTH)
                        curve = [(rect.left + 4, cy + Constants.ISOLATION_WIDTH // 2), 
                            (rect.left + 4, cy - (Constants.ISOLATION_WIDTH - 1 ) // 2),
                            (cx - (Constants.ISOLATION_WIDTH - 1 ) // 2, rect.top + 4),
                            (cx + Constants.ISOLATION_WIDTH // 2, rect.top + 4), 
                        ]
                        pygame.draw.polygon(surface, Constants.TRACK_COLOR, curve)
                elif "TrainEnd_" in elem_name:
                    if "West" in elem_name:
                        points = [(cx + tileSizeHalf - 10, cy - tileSizeHalf + 10), 
                            (cx + tileSizeHalf - 10, cy + tileSizeHalf - 10), 
                            (cx - tileSizeHalf + 10, cy)]
                        pygame.draw.polygon(surface, Constants.TRACK_COLOR, points)
                    elif "East" in elem_name:
                        points = [(cx - tileSizeHalf + 10, cy - tileSizeHalf + 10), 
                            (cx - tileSizeHalf + 10, cy + tileSizeHalf - 10), 
                            (cx + tileSizeHalf - 10, cy)]
                        pygame.draw.polygon(surface, Constants.TRACK_COLOR, points)
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
                        pygame.draw.polygon(surface, Constants.TRACK_COLOR, points, 2)
                    elif "East" in elem_name:
                        points = [(cx - tileSizeHalf + 8, cy - tileSizeHalf + 8), 
                            (cx - tileSizeHalf + 8, cy + tileSizeHalf - 8), 
                            (cx + tileSizeHalf - 8, cy)]
                        pygame.draw.polygon(surface, Constants.TRACK_COLOR, points, 2)
                if "TextLabels" in element:
                    labels = element["TextLabels"]
                    label_text = labels.get("Number", labels.get("Index", labels.get("IsolationName", labels.get("StationName" ))))
                    direction = labels.get( "MainDirection")
                    if label_text:
                        if "StationName" in labels:
                            text_surf = self.font_title.render(label_text, True, Constants.TRACK_COLOR)
                            text_rect = text_surf.get_rect(center=(cx, cy))
                            surface.blit(text_surf, text_rect)
                        elif "Isolation_Shortened_Horizontal_Number" == elem_name:
                            text_surf = self.small_font.render(str(label_text), True, Constants.TRACK_COLOR)
                            text_rect = text_surf.get_rect(center=(cx, cy - 10))
                            surface.blit(text_surf, text_rect)
                        elif "Sem" in elem_name or "To_" in elem_name or "ShuntEnd" in elem_name:
                            color = ( "OnlyShunt" in elem_name or "ShuntEnd" in elem_name ) and (0, 255, 255) or (255, 255, 0)
                            text_surf = self.sem_font.render(str(label_text), True, color)
                            text_rect = text_surf.get_rect(center=(cx, cy + 18))
                            surface.blit(text_surf, text_rect)
                        elif "SignalReapeter" in elem_name:
                            text_surf = self.sem_font.render(str(label_text), True, Constants.TRACK_COLOR)
                            text_rect = text_surf.get_rect(center=(cx, cy + 18))
                            surface.blit(text_surf, text_rect)
                        elif "Platform" in elem_name:
                            sign = "South" in elem_name and -1 or 1
                            text_surf = self.font.render(str(label_text), True, Constants.TRACK_COLOR)
                            text_rect = text_surf.get_rect(center=(cx, cy + sign * ("Horizontal" in elem_name and -1 or 5)))
                            surface.blit(text_surf, text_rect)
                        elif "LineBlockNew" == elem_name:
                            text_surf = self.sem_font.render(str(label_text), True, (255, 255, 0))
                            text_rect = text_surf.get_rect(center=(cx, rect.top - 10))
                            surface.blit(text_surf, text_rect)
                        elif "Point_South" in elem_name:
                            text_surf = self.small_font.render(f"{label_text} {direction}", True, Constants.TRACK_COLOR)
                            text_rect = text_surf.get_rect(center=(cx, cy - 10))
                            surface.blit(text_surf, text_rect)
                        elif "Point_North" in elem_name:
                            text_surf = self.small_font.render(f"{label_text} {direction}", True, Constants.TRACK_COLOR)
                            text_rect = text_surf.get_rect(center=(cx, cy + 10))
                            surface.blit(text_surf, text_rect)
                        elif "Crossing_North" == elem_name:
                            text_surf = self.small_font.render(str(label_text), True, Constants.TRACK_COLOR)
                            text_rect = text_surf.get_rect(center=(cx, cy - 20))
                            surface.blit(text_surf, text_rect)
                        elif "Crossing_South" == elem_name:
                            text_surf = self.small_font.render(str(label_text), True, Constants.TRACK_COLOR)
                            text_rect = text_surf.get_rect(center=(cx, cy + 20))
                            surface.blit(text_surf, text_rect)
                        elif "Derailer_North" == elem_name:
                            text_surf = self.sem_font.render(str(label_text), True, (255,255,255))
                            text_rect = text_surf.get_rect(center=(cx, cy - 18))
                            surface.blit(text_surf, text_rect)
                        elif number_text := labels.get("NumberText", ""):
                            text_surf = self.small_font.render(str(number_text), True, Constants.TRACK_COLOR)
                            text_rect = text_surf.get_rect(center=(real_cx, cy))
                            bg_rect = pygame.Rect( text_rect.left - 6, text_rect.top - 4, text_rect.width + 6 * 2, text_rect.height + 4 * 2 )
                            pygame.draw.rect(surface, (0, 0, 0), bg_rect)            
                            surface.blit(text_surf, text_rect)
            if pressed_pos and rect.collidepoint( pressed_pos ):
                if not "Platform" in elem_name and not "Vertical" in elem_name and not "Curve" in elem_name:
                    pygame.draw.rect(surface, (0, 255, 255), rect, 2, 4) 
            elif mouse_pos and rect.collidepoint(mouse_pos):
                if not "Platform" in elem_name and not "Vertical" in elem_name and not "Curve" in elem_name:
                    pygame.draw.rect(surface, (255, 255, 0), rect, 2, 4) 