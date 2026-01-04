import pygame
import pygame_gui
import pygame_gui.elements as pygame_elements
from pygame_gui.core import ObjectID
from constants import Constants
import maps
from elements.track_elements import TrackElement
from elements.train_spawner import TrainSpawner
from typing import List, Tuple, Dict

def create_main_menu(manager: pygame_gui.UIManager) -> Tuple[pygame_elements.UIButton, pygame_elements.UIButton]:
    center_x = Constants.MAIN_WIN_WIDTH // 2
    center_y = Constants.MAIN_WIN_HEIGHT // 2
    
    pygame_elements.UILabel(
        relative_rect=pygame.Rect(center_x - 500, center_y - 200, 1000, 120),
        text="SYMULATOR LCS",
        manager=manager,
        object_id=ObjectID(class_id='@title_label')
    )
    
    play_button = pygame_elements.UIButton(
        relative_rect=pygame.Rect(center_x - Constants.BUTTON_WIDTH // 2, center_y - Constants.BUTTON_HEIGHT // 2 - 5, Constants.BUTTON_WIDTH, Constants.BUTTON_HEIGHT),
        text='Graj', manager=manager
    )
    
    leaderboard_button = pygame_elements.UIButton(
        relative_rect=pygame.Rect(center_x - Constants.BUTTON_WIDTH // 2, center_y + Constants.BUTTON_HEIGHT // 2 + 5, Constants.BUTTON_WIDTH, Constants.BUTTON_HEIGHT),
        text='Wyniki', manager=manager
    )
    
    return play_button, leaderboard_button

def create_leaderboard_menu(manager: pygame_gui.UIManager, results : Dict[str, int]) -> pygame_elements.UIButton:
    center_x = Constants.MAIN_WIN_WIDTH // 2
    center_y = Constants.MAIN_WIN_HEIGHT // 2
    
    pygame_elements.UILabel(
        relative_rect=pygame.Rect(center_x - 400, center_y - 200, 800, 120),
        text="WYNIKI",
        manager=manager,
        object_id=ObjectID(class_id='@title_label')
    )
    
    y_offset = 50
    for map, score in results.items():
        panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(center_x - 100, center_y - y_offset, 200, 30),
            manager=manager,
        )
        pygame_elements.UILabel(
            relative_rect=pygame.Rect(0, 0, 200, 24),
            text=f"{map.replace('_', ' ').title()}: {score}",
            manager=manager,
            container = panel,
            object_id=ObjectID(class_id='@result_label')
        )
        y_offset -= 35
    
    return_button = pygame_elements.UIButton(
        relative_rect=pygame.Rect(center_x - Constants.BUTTON_WIDTH // 2, center_y - y_offset + Constants.BUTTON_HEIGHT // 2 + 5, Constants.BUTTON_WIDTH, Constants.BUTTON_HEIGHT),
        text='Wróc', manager=manager
    )
    
    return return_button

def create_maps_menu(manager: pygame_gui.UIManager, selected_map: str) -> Tuple[pygame_gui.elements.UIImage, pygame_elements.UILabel]:
    center_x = Constants.MAIN_WIN_WIDTH // 2
    center_y = Constants.MAIN_WIN_HEIGHT // 2
    
    offset = 150
    
    icon = pygame.image.load(f"assets/{selected_map}.png").convert_alpha()
    if icon:
        map_image = pygame_gui.elements.UIImage(
            relative_rect=pygame.Rect(center_x - 400, center_y - 500 + offset, 800, 400), 
            manager=manager,
            image_surface = icon
        )
    
    pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(center_x - Constants.BUTTON_WIDTH // 2 - 50, center_y - Constants.BUTTON_HEIGHT * 2 - 5 + offset, 50, 50), 
        text="<", manager=manager
    )
    
    pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(center_x + Constants.BUTTON_WIDTH // 2, center_y - Constants.BUTTON_HEIGHT * 2 - 5 + offset, 50, 50), 
        text=">", manager=manager
    )
    
    map_label = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect(center_x - Constants.BUTTON_WIDTH // 2, center_y - Constants.BUTTON_HEIGHT * 2 - 5 + offset, Constants.BUTTON_WIDTH, Constants.BUTTON_HEIGHT ),
        text=selected_map.replace("_", " ").title(), manager=manager,
        object_id=ObjectID(class_id='@map_label')
    )

    pygame_elements.UIButton(
        relative_rect=pygame.Rect(center_x - Constants.BUTTON_WIDTH // 2, center_y - Constants.BUTTON_HEIGHT // 2 - 5 + offset, Constants.BUTTON_WIDTH, Constants.BUTTON_HEIGHT),
        text="Uruchom", manager=manager,
        object_id=ObjectID(object_id='#start_button')
    )
    
    pygame_elements.UIButton(
        relative_rect=pygame.Rect(center_x - Constants.BUTTON_WIDTH // 2, center_y + Constants.BUTTON_HEIGHT // 2 + 5 + offset, Constants.BUTTON_WIDTH, Constants.BUTTON_HEIGHT),
        text="Powrót", manager=manager
    )

    return map_image, map_label


def create_settings_menu(manager: pygame_gui.UIManager) -> None:
    pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((Constants.MAIN_WIN_WIDTH - 150) // 2, 300, 150, 40 ),
        text="Powrót", manager=manager
    )
    
def create_pause_menu(manager: pygame_gui.UIManager) -> Tuple[pygame_elements.UIButton, pygame_elements.UIButton]:    
    center_x = Constants.MAIN_WIN_WIDTH // 2
    center_y = Constants.MAIN_WIN_HEIGHT // 2
    
    pygame_elements.UILabel(
        relative_rect=pygame.Rect(center_x - 200, center_y - 200, 400, 200),
        text="PAUZA",
        manager=manager,
        object_id=ObjectID(class_id='@pause_label')
    )
    
    resume_button = pygame_elements.UIButton(
        relative_rect=pygame.Rect(center_x - Constants.BUTTON_WIDTH // 2, center_y - Constants.BUTTON_HEIGHT // 2 - 5, Constants.BUTTON_WIDTH, Constants.BUTTON_HEIGHT),
        text='Wznów', manager=manager
    )
    
    main_menu_button = pygame_elements.UIButton(
        relative_rect=pygame.Rect(center_x - Constants.BUTTON_WIDTH // 2, center_y + Constants.BUTTON_HEIGHT // 2 + 5, Constants.BUTTON_WIDTH, Constants.BUTTON_HEIGHT),
        text="Zakończ grę i menu", manager=manager
    )
    
    return resume_button, main_menu_button

def create_actions_menu(manager: pygame_gui.UIManager, track_element : TrackElement) -> List[pygame_gui.elements.UIButton]:
    font = pygame.font.Font(pygame.font.get_default_font(),)
    panel_width = sum([font.size(action_name)[0] + 5 for action_name in track_element.actions.keys()]) + 10 

    buttons = []
    x_offset = ( Constants.MAIN_WIN_WIDTH - panel_width ) // 2 + 5
    for action_name in track_element.actions.keys():
        width = font.size(action_name)[0] + 5
        button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(x_offset, 5, width, 30),
            text=action_name,
            manager=manager,
            object_id=ObjectID(class_id='@actions_button')
        )
        
        button.user_data = {"object": track_element, "action": action_name}
        buttons.append(button)
        x_offset += width
    
    return buttons

def create_train_spawner_menu(manager: pygame_gui.UIManager, spawner: TrainSpawner):
    if len(spawner.waiting_trains) == 0:
        return
    
    panel_width = 300
    panel_height = len(spawner.waiting_trains) * 40 + 15
    panel_rect = pygame.Rect(((Constants.MAIN_WIN_WIDTH - panel_width) // 2, 5), 
                             (panel_width, panel_height))

    menu_panel = pygame_gui.elements.UIPanel(
        relative_rect=panel_rect,
        manager=manager,
    )

    buttons = []
    y_offset = 10
    for train in spawner.waiting_trains:
        button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, y_offset, panel_width - 20, 30),
            text=f"{train.get_train_type_name().title()} -> {train.destination}",
            manager=manager,
            container=menu_panel,
            object_id=ObjectID(class_id='@trains_button', object_id=spawner.delayed and '#delayed_spawner_button' or ''),
        )
        
        button.user_data = {"object": spawner, "action": "select_train", "train": train}
        buttons.append(button)
        y_offset += 40

def create_game_over_menu(manager: pygame_gui.UIManager) -> pygame_elements.UIButton:
    center_x = Constants.MAIN_WIN_WIDTH // 2
    center_y = Constants.MAIN_WIN_HEIGHT // 2
    
    pygame_elements.UILabel(
        relative_rect=pygame.Rect(center_x - 300, center_y - 200, 600, 100),
        text="KONIEC GRY",
        manager=manager,
        object_id=ObjectID(class_id='@game_over_label')
    )
    pygame_elements.UILabel(
        relative_rect=pygame.Rect(center_x - 200, center_y - 100, 400, 50),
        text="PRZEGRAŁES",
        manager=manager,
        object_id=ObjectID(class_id='@lost_label')
    )
    
    return_button = pygame_elements.UIButton(
        relative_rect=pygame.Rect(center_x - Constants.BUTTON_WIDTH // 2, center_y, Constants.BUTTON_WIDTH, Constants.BUTTON_HEIGHT),
        text="Powrót do menu", manager=manager
    )
    
    return return_button

