import pygame
from constants import Constants
import pygame_gui
import interface
import maps
from maps import Maps
from simulation.simulator import Simulator
from simulation.renderer import GameRenderer
import stations.brzozowa_dolina, stations.kamieniec, stations.nowe_zelazno

def main_loop(window_surface : pygame.surface):
    clock: pygame.time.Clock = pygame.time.Clock()
    
    ui_manager: pygame_gui.UIManager = pygame_gui.UIManager((Constants.MAIN_WIN_WIDTH, Constants.MAIN_WIN_HEIGHT), theme_path="assets/theme.json")
    
    running: bool = True
    state: str = "menu"
    
    simulator = Simulator()
    renderer = GameRenderer()
    
    play_button, leaderboard_button, settings_button = interface.create_main_menu(ui_manager)
    map_index = 0
    
    camera_x = Constants.GRID_OFFSET_X
    camera_y = Constants.GRID_OFFSET_Y
    
    is_dragging = False
    last_mouse_pos = (0, 0)
    
    selected_positions = []
    
    while running:
        time_delta: float = clock.tick(Constants.FPS_LIMIT) / 1000.0
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if state == "game":
                        state = "pause"
                        resume_button, exit_to_menu_button = interface.create_pause_menu(ui_manager)
                    elif state == "pause":
                        state = "game"
                        ui_manager.clear_and_reset()
            ui_manager.process_events(event)
                        
            if state == "game":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        clicked_pos = f"{(event.pos[0] - camera_x) // Constants.TILE_SIZE}-{(event.pos[1] - camera_y) // Constants.TILE_SIZE}" 
                        
                        mods = pygame.key.get_mods()
                        if mods & pygame.KMOD_CTRL:
                            if clicked_pos in selected_positions:
                                selected_positions.remove(clicked_pos)
                            elif len(selected_positions) < 2:
                                selected_positions.append(clicked_pos)
                        else:
                            selected_positions = [clicked_pos]
                
                        selected_object = simulator.logical_elements.get(clicked_pos)
                        if selected_object:
                            if len(selected_object.actions) == 0:
                                ui_manager.clear_and_reset()
                            else:
                                panel, action_buttons = interface.create_actions_menu(ui_manager, selected_object)
                    if event.button == 2:
                        is_dragging = True
                        last_mouse_pos = event.pos
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 2:
                        is_dragging = False
                elif event.type == pygame.MOUSEMOTION:
                    if is_dragging:
                        mx, my = event.pos
                        dx = mx - last_mouse_pos[0]
                        dy = my - last_mouse_pos[1]
                        camera_x += dx
                        camera_y += dy
                        last_mouse_pos = (mx, my)
            
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if state == "menu":
                    if event.ui_element == play_button:
                        ui_manager.clear_and_reset()
                        state = "map_select"
                        map_label = interface.create_maps_menu(ui_manager)
                    elif event.ui_element == settings_button:
                        ui_manager.clear_and_reset()
                        print("TODO")
                        state = "settings"
                elif state == "map_select":
                    if event.ui_element.text == ">":
                        map_index = (map_index + 1) % len(maps.get_available_maps())
                        map_label.set_text(maps.get_available_maps()[map_index])
                    elif event.ui_element.text == "<":
                        map_index = (map_index - 1) % len(maps.get_available_maps())
                        map_label.set_text(maps.get_available_maps()[map_index])
                    elif event.ui_element.text == "Powrót":
                        ui_manager.clear_and_reset()
                        state = "menu"
                        play_button, leaderboard_button, settings_button = interface.create_main_menu(ui_manager)
                    elif event.ui_element.text == "Uruchom":
                        ui_manager.clear_and_reset()
                        state = "game"
                        camera_x = Constants.GRID_OFFSET_X
                        camera_y = Constants.GRID_OFFSET_Y
                        map = Maps(maps.get_available_maps()[map_index])
                        simulator.load_map(map.schema)
                elif state == "game":
                    if hasattr(event.ui_element, 'user_data'):
                        data = event.ui_element.user_data
                        point_object = data["object"]
                        action_name = data["action"]
                        
                        point_object.execute_action(action_name)
                        ui_manager.clear_and_reset()
                elif state == "pause":
                    if event.ui_element == resume_button:
                        state = "game"
                        ui_manager.clear_and_reset()
                    elif event.ui_element == exit_to_menu_button:
                        state = "menu"
                        ui_manager.clear_and_reset()
                        simulator = Simulator() 
                        play_button, leaderboard_button, settings_button = interface.create_main_menu(ui_manager)
                elif state == "settings":
                    pass
                
        window_surface.fill((0, 0, 0))
        
        if simulator is not None:
            simulator.update()
        
        if state == "game":
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                camera_x += Constants.CAMERA_MOVE_SPEED * time_delta
            if keys[pygame.K_RIGHT]:
                camera_x -= Constants.CAMERA_MOVE_SPEED * time_delta
            if keys[pygame.K_UP]:
                camera_y += Constants.CAMERA_MOVE_SPEED * time_delta
            if keys[pygame.K_DOWN]:
                camera_y -= Constants.CAMERA_MOVE_SPEED * time_delta

            mouse_pos = pygame.mouse.get_pos()
            
            renderer.draw_map(window_surface, simulator, (camera_x, camera_y), mouse_pos, selected_positions)
            
        ui_manager.update(time_delta)
        ui_manager.draw_ui(window_surface)
        
        pygame.display.update()