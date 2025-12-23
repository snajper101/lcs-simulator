import pygame
from constants import Constants

class GameRenderer:
    def __init__(self):
        self.font = pygame.font.SysFont("Arial", 10)
        
    def draw_map(self, surface: pygame.Surface, map_data: dict ) -> None:
        surface.fill(Constants.BG_COLOR)
        
        for coord_str, elements in map_data.items():
            grid_x, grid_y = map(int, coord_str.split('-'))
            
            screen_x = Constants.GRID_OFFSET_X + (grid_x * Constants.TILE_SIZE)
            screen_y = Constants.GRID_OFFSET_Y + (grid_y * Constants.TILE_SIZE)
            
            rect = pygame.Rect(screen_x, screen_y, Constants.TILE_SIZE, Constants.TILE_SIZE)

            for element in elements:
                elem_name = element.get("Name", "")
                
                if "Horizontal" in elem_name:
                    start_pos = (screen_x, screen_y + Constants.TILE_SIZE // 2)
                    end_pos = (screen_x + Constants.TILE_SIZE, screen_y + Constants.TILE_SIZE // 2)
                    pygame.draw.line(surface, Constants.TRACK_COLOR, start_pos, end_pos, 3)
                    
                    if "Isolation" in elem_name:
                        pygame.draw.line(surface, (255, 0, 0), 
                                         (screen_x + 2, screen_y + 10), 
                                         (screen_x + 2, screen_y + Constants.TILE_SIZE - 10), 2)

                elif "Vertical" in elem_name:
                    start_pos = (screen_x + Constants.TILE_SIZE // 2, screen_y)
                    end_pos = (screen_x + Constants.TILE_SIZE // 2, screen_y + Constants.TILE_SIZE)
                    pygame.draw.line(surface, Constants.TRACK_COLOR, start_pos, end_pos, 3)

                elif "Point" in elem_name:
                    pygame.draw.circle(surface, (100, 100, 255), rect.center, 5)

                elif "Sem" in elem_name:
                    sem_color = (0, 255, 0)
                    pygame.draw.rect(surface, sem_color, (screen_x + 10, screen_y + 10, 12, 12))

                if "TextLabels" in element:
                    labels = element["TextLabels"]
                    label_text = labels.get("Number", labels.get("IsolationName", ""))
                    if label_text:
                        text_surf = self.font.render(label_text, True, (200, 200, 200))
                        surface.blit(text_surf, (screen_x, screen_y - 10))