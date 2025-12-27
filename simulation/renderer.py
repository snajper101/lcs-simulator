import pygame
from constants import Constants

class GameRenderer:
    def __init__(self):
        self.font = pygame.font.SysFont("Arial", 12, bold=True)
        self.small_font = pygame.font.SysFont("Arial", 10)
        self.sem_font = pygame.font.SysFont("Arial", 14, bold=True)
        
    def draw_map(self, surface: pygame.Surface, map_data: dict, camera_offset: tuple, mouse_pos: tuple = None) -> None:
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

            for element in elements:
                elem_name = element.get("Name", "")
                if elem_name == "Non_Isolated_Horizontal":
                    start_pos = (rect.left + 4, cy)
                    end_pos = (rect.right - 4, cy)
                    pygame.draw.line(surface, Constants.TRACK_COLOR, start_pos, end_pos, Constants.LINE_ISOLATION_WIDTH)
                elif "Horizontal" in elem_name:
                    start_pos = (rect.left + 4, cy)
                    end_pos = (rect.right - 4, cy)
                    pygame.draw.line(surface, Constants.TRACK_COLOR, start_pos, end_pos, Constants.ISOLATION_WIDTH)
                elif "Vertical" in elem_name:
                    start_pos = (cx, rect.top)
                    end_pos = (cx, rect.bottom)
                    pygame.draw.line(surface, Constants.TRACK_COLOR, start_pos, end_pos, Constants.ISOLATION_WIDTH)
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
                elif "Point" in elem_name:
                    pygame.draw.line(surface, Constants.TRACK_COLOR, (rect.left, cy), (rect.right, cy), 3)
                    if "North_East" in elem_name:
                        pygame.draw.line(surface, Constants.TRACK_COLOR, (cx, cy), (rect.right, rect.top), 3)
                    elif "South_East" in elem_name:
                        pygame.draw.line(surface, Constants.TRACK_COLOR, (cx, cy), (rect.right, rect.bottom), 3)
                    elif "North_West" in elem_name:
                        pygame.draw.line(surface, Constants.TRACK_COLOR, (cx, cy), (rect.left, rect.top), 3)
                    elif "South_West" in elem_name:
                        pygame.draw.line(surface, Constants.TRACK_COLOR, (cx, cy), (rect.left, rect.bottom), 3)

                elif "Sem" in elem_name:
                    tileSizeHalf = Constants.TILE_SIZE // 2
                    if "West" in elem_name:
                        points = [(cx + tileSizeHalf - 8, cy - tileSizeHalf + 8), 
                            (cx + tileSizeHalf - 8, cy + tileSizeHalf - 8), 
                            (cx - tileSizeHalf + 8, cy)]
                        pygame.draw.polygon(surface, Constants.TRACK_COLOR, points)
                    elif "East" in elem_name:
                        points = [(cx - tileSizeHalf + 8, cy - tileSizeHalf + 8), 
                            (cx - tileSizeHalf + 8, cy + tileSizeHalf - 8), 
                            (cx + tileSizeHalf - 8, cy)]
                        pygame.draw.polygon(surface, Constants.TRACK_COLOR, points)
                    else:
                        pygame.draw.rect(surface, Constants.TRACK_COLOR, (screen_x + 10, screen_y + 10, 12, 12))

                elif "LineBlock" in elem_name or "To_" in elem_name or "TrainEnd" in elem_name:
                     pygame.draw.circle(surface, (100, 100, 255), (cx, cy), 4)

                if "TextLabels" in element:
                    labels = element["TextLabels"]
                    label_text = labels.get("Number", labels.get("Index", labels.get("IsolationName", labels.get("StationName", ""))))
                    if label_text:
                        if "StationName" in labels:
                            text_surf = self.font.render(label_text, True, (255, 255, 255))
                            text_rect = text_surf.get_rect(center=(cam_x + surface.get_width() // 2, rect.top - 15))
                            surface.blit(text_surf, text_rect)
                        elif "Isolation_Shortened_Horizontal_Number" in elem_name:
                            text_surf = self.small_font.render(str(label_text), True, Constants.TRACK_COLOR)
                            text_rect = text_surf.get_rect(center=(cx, cy - 10))
                            surface.blit(text_surf, text_rect)
                        elif "Sem" in elem_name or "To_" in elem_name:
                            text_surf = self.sem_font.render(str(label_text), True, (255, 255, 0))
                            text_rect = text_surf.get_rect(center=(cx, cy + 20))
                            surface.blit(text_surf, text_rect)
                        elif "Platform" in elem_name:
                            text_surf = self.font.render(str(label_text), True, Constants.TRACK_COLOR)
                            text_rect = text_surf.get_rect(center=(cx, cy + ( "North" in elem_name and 5 or - 5 )))
                            surface.blit(text_surf, text_rect)

            if mouse_pos and rect.collidepoint(mouse_pos):
                if not "Platform" in elem_name:
                    pygame.draw.rect(surface, (255, 255, 0), rect, 2)