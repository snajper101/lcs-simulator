import pygame
from constants import Constants
import pygame_gui
import interface
import maps
from maps import Maps
from simulation.simulator import Simulator
from simulation.renderer import GameRenderer
from elements.semaphore import Semaphore
from elements.train_spawner import TrainSpawner
from effects import DotGridBackground
from profiles.data_manager import DataStore

def main_loop(window_surface : pygame.surface, data_store: DataStore):
    clock: pygame.time.Clock = pygame.time.Clock()
    
    ui_manager: pygame_gui.UIManager = pygame_gui.UIManager((Constants.MAIN_WIN_WIDTH, Constants.MAIN_WIN_HEIGHT), theme_path="assets/theme.json")
    
    running: bool = True
    state: str = "menu"
    
    simulator = Simulator()
    renderer = GameRenderer()
    
    background_effect = DotGridBackground(spacing=20, dot_radius=2)
    
    play_button, leaderboard_button = interface.create_main_menu(ui_manager)
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
                        selected_object = simulator.logical_elements.get(clicked_pos)
                        if not selected_object:
                            for obj in simulator.logical_elements.values():
                                if isinstance(obj, TrainSpawner) and hasattr(obj, 'hit_box'):
                                    if obj.hit_box.collidepoint(event.pos):
                                        selected_object = obj
                                        clicked_pos = f"{obj.tracks[0].position[0]}-{obj.tracks[0].position[1]}"
                                        break
                               
                        if not ui_manager.get_hovering_any_element():          
                            mods = pygame.key.get_mods()
                            if mods & pygame.KMOD_CTRL:
                                if clicked_pos in selected_positions:
                                    selected_positions.remove(clicked_pos)
                                elif len(selected_positions) < 2:
                                    selected_positions.append(clicked_pos)       
                                    if len(selected_positions) == 2:
                                        first_object = simulator.logical_elements.get(selected_positions[0])
                                        second_object = simulator.logical_elements.get(selected_positions[1])
                                        if isinstance(first_object, Semaphore) and isinstance(second_object, Semaphore):
                                            first_object.set_advance_selected_signal(second_object)
                                            ui_manager.clear_and_reset()
                                            interface.create_actions_menu(ui_manager, first_object)
                            else:
                                selected_positions = [clicked_pos]
                                if selected_object:
                                    ui_manager.clear_and_reset()
                                    if isinstance(selected_object, TrainSpawner):
                                        interface.create_train_spawner_menu(ui_manager, selected_object)
                                    elif hasattr(selected_object, "actions") and len(selected_object.actions) > 0:
                                        interface.create_actions_menu(ui_manager, selected_object)        
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
                        map_index = 0
                        map_image, map_label = interface.create_maps_menu(ui_manager, maps.get_available_maps()[map_index])
                    elif event.ui_element == leaderboard_button:
                        ui_manager.clear_and_reset()
                        state = "leaderboard"
                        leaderboard_return = interface.create_leaderboard_menu(ui_manager, data_store.get_results())
                elif state == "map_select":
                    if event.ui_element.text == ">":
                        map_index = (map_index + 1) % len(maps.get_available_maps())
                        map_str = maps.get_available_maps()[map_index].replace("_", " ").title()
                        icon = pygame.image.load(f"assets/{maps.get_available_maps()[map_index]}.png").convert_alpha()
                        map_image.set_image(icon)
                        map_label.set_text(map_str)
                    elif event.ui_element.text == "<":
                        map_index = (map_index - 1) % len(maps.get_available_maps())
                        map_str = maps.get_available_maps()[map_index].replace("_", " ").title()
                        icon = pygame.image.load(f"assets/{maps.get_available_maps()[map_index]}.png").convert_alpha()
                        map_image.set_image(icon)
                        map_label.set_text(map_str)
                    elif event.ui_element.text == "Powrót":
                        ui_manager.clear_and_reset()
                        state = "menu"
                        play_button, leaderboard_button = interface.create_main_menu(ui_manager)
                    elif event.ui_element.text == "Uruchom":
                        ui_manager.clear_and_reset()
                        state = "game"
                        camera_x = Constants.GRID_OFFSET_X
                        camera_y = Constants.GRID_OFFSET_Y
                        simulator.load_map(Maps(maps.get_available_maps()[map_index]))
                elif state == "game":
                    if hasattr(event.ui_element, 'user_data'):
                        data = event.ui_element.user_data
                        point_object = data["object"]
                        action_name = data["action"]
                        
                        if action_name == "select_train":
                            train = data["train"]
                            spawner : TrainSpawner = point_object
                            spawner.add_train_to_line(train, [track for track in spawner.tracks if track.normal][0])
                        else:
                            point_object.execute_action(action_name)
                            ui_manager.clear_and_reset()
                elif state == "pause":
                    if event.ui_element == resume_button:
                        state = "game"
                        ui_manager.clear_and_reset()
                    elif event.ui_element == exit_to_menu_button:
                        state = "menu"
                        ui_manager.clear_and_reset()
                        data_store.add_result(simulator.map.map, simulator.user_points)
                        simulator = Simulator() 
                        play_button, leaderboard_button = interface.create_main_menu(ui_manager)
                elif state == "game_over":
                    if event.ui_element == game_over_return_button:
                        state = "menu"
                        ui_manager.clear_and_reset()

                        simulator = Simulator() 
                        play_button, leaderboard_button = interface.create_main_menu(ui_manager)
                elif state == "leaderboard":
                    if event.ui_element == leaderboard_return:
                        state = "menu"
                        ui_manager.clear_and_reset()
                        play_button, leaderboard_button = interface.create_main_menu(ui_manager)
                
        background_effect.update(time_delta)
                
        window_surface.fill((0, 0, 0))
        if state in ["menu", "settings", "map_select", "game_over", "pause", "leaderboard"]:
            background_effect.draw(window_surface)
        
        if simulator is not None and state != "game_over":
            simulator.update(time_delta)
        
        if state == "game":
            if simulator.user_points < 0:
                state = "game_over"
                game_over_return_button = interface.create_game_over_menu(ui_manager)
            else:
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
                
                renderer.draw_map(window_surface, ui_manager, simulator, (camera_x, camera_y), mouse_pos, selected_positions)
            
        ui_manager.update(time_delta)
        ui_manager.draw_ui(window_surface)
        
        pygame.display.update()