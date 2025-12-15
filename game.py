import pygame
import constants
import pygame_gui
import interface
import maps

def main_loop(window_surface : pygame.surface):
    clock: pygame.time.Clock = pygame.time.Clock()
    
    ui_manager: pygame_gui.UIManager = pygame_gui.UIManager((constants.MAIN_WIN_WIDTH, constants.MAIN_WIN_HEIGHT), theme_path="assets/theme.json")
    
    running: bool = True
    state: str = "menu"
    
    play_button, leaderboard_button, settings_button = interface.create_main_menu(ui_manager)
    map_index = 0
    
    while running:
        time_delta: float = clock.tick(constants.FPS_LIMIT) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            ui_manager.process_events(event)
            
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if state == "menu":
                    if event.ui_element == play_button:
                        ui_manager.clear_and_reset()
                        state = "map_select"
                        map_label = interface.create_maps_menu(ui_manager)
                    elif event.ui_element == settings_button:
                        print("TODO")
                        state = "settings"
                elif state == "map_select":
                    if event.ui_element.text == ">":
                        map_index = (map_index + 1) % len(maps.MAPS)
                        map_label.set_text(maps.MAPS[map_index])
                    elif event.ui_element.text == "<":
                        map_index = (map_index - 1) % len(maps.MAPS)
                        map_label.set_text(maps.MAPS[map_index])
                    elif event.ui_element.text == "Powrót":
                        ui_manager.clear_and_reset()
                        state = "menu"
                        play_button, leaderboard_button, settings_button = interface.create_main_menu(ui_manager)
                elif state == "game":
                    pass
                
        window_surface.fill((0, 0, 0))
        
        ui_manager.update(time_delta)
        ui_manager.draw_ui(window_surface)
        
        pygame.display.update()
            
        
        