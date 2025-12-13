import pygame
import constants
import pygame_gui
from interface import create_main_menu

def main_loop(window_surface : pygame.surface):
    clock: pygame.time.Clock = pygame.time.Clock()
    menu_manager: pygame_gui.UIManager = pygame_gui.UIManager((constants.MAIN_WIN_WIDTH, constants.MAIN_WIN_HEIGHT), theme_path="theme.json")
    game_manager: pygame_gui.UIManager = pygame_gui.UIManager((constants.MAIN_WIN_WIDTH, constants.MAIN_WIN_HEIGHT), theme_path="theme.json")
    
    running: bool = True
    state: str = "menu"
    
    play_button, settings_button = create_main_menu(menu_manager)
    
    while running:
        time_delta: float = clock.tick(constants.FPS_LIMIT) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            if state == "menu":
                menu_manager.process_events(event)
                
                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == play_button:
                        state = "game"
                    if event.ui_element == settings_button:
                        state = "settings"
            elif state == "game":
                game_manager.process_events(event)
                
        if state == "menu":
            menu_manager.update(time_delta)
            menu_manager.draw_ui(window_surface)
        elif state == "game":
            game_manager.update(time_delta)
            window_surface.fill((40, 120, 40))
        
        pygame.display.update()
            
        
        