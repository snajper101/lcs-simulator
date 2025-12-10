import pygame
import constants
import pygame_gui

def main_loop():
    clock: pygame.time.Clock = pygame.time.Clock()
    manager: pygame_gui.UIManager = pygame_gui.UIManager((800, 600))
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        clock.tick(constants.FPS_LIMIT)