import pygame
import math
from constants import Constants

class DotGridBackground:
    def __init__(self, spacing: int, dot_radius: int):
        self.spacing = spacing
        self.radius = dot_radius
        self.time = 0.0
        
        self.min_brightness = 20
        self.max_brightness = 120
        
        self.cols = (Constants.MAIN_WIN_WIDTH // spacing) + 2
        self.rows = (Constants.MAIN_WIN_HEIGHT // spacing) + 2
        self.positions = []
        
        for x in range(self.cols):
            for y in range(self.rows):
                self.positions.append((x * spacing, y * spacing))

    def update(self, time_delta: float):
        self.time += time_delta * 2.5
        if self.time > math.pi * 2:
            self.time = 0

    def draw(self, surface: pygame.Surface):
        for x, y in self.positions:
            val1 = math.sin(x * 0.1 + self.time)
            val2 = math.cos(y * 0.1 + self.time)
            val3 = math.sin(x * 0.05 + y * 0.05 + self.time)
            
            noise_val = (val1 + val2 + val3) / 3
            
            brightness = int(((noise_val + 1) / 2) * (self.max_brightness - self.min_brightness) + self.min_brightness)
            
            color = (brightness, brightness, brightness)
            
            pygame.draw.circle(surface, color, (x, y), self.radius)