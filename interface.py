import pygame
import pygame_gui
import pygame_gui.elements as pygame_elements
from constants import Constants
import maps
from elements.track_elements import TrackElement
from typing import List

def create_main_menu(manager: pygame_gui.UIManager) -> tuple[pygame_elements.UIButton, pygame_elements.UIButton, pygame_elements.UIButton]:
    play_button = pygame_elements.UIButton(
        relative_rect=pygame.Rect((Constants.MAIN_WIN_WIDTH - Constants.BUTTON_WIDTH) // 2, (Constants.MAIN_WIN_HEIGHT - 2 * Constants.BUTTON_HEIGHT) // 2, 150, 40),
        text='Graj', manager=manager
    )
    
    leaderboard_button = pygame_elements.UIButton(
        relative_rect=pygame.Rect((Constants.MAIN_WIN_WIDTH - Constants.BUTTON_WIDTH) // 2, (Constants.MAIN_WIN_HEIGHT) // 2, 150, 40),
        text='Wyniki', manager=manager
    )
    
    settings_button = pygame_elements.UIButton(
        relative_rect=pygame.Rect((Constants.MAIN_WIN_WIDTH - Constants.BUTTON_WIDTH) // 2, (Constants.MAIN_WIN_HEIGHT + 2 * Constants.BUTTON_HEIGHT) // 2, 150, 40),
        text='Ustawienia', manager=manager
    )
    
    return ( play_button, leaderboard_button, settings_button )

def create_maps_menu(manager: pygame_gui.UIManager) -> pygame_elements.UIButton:
    pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(200, 200, 50, 50), text="<", manager=manager
    )
    
    pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect(550, 200, 50, 50), text=">", manager=manager
    )
    
    map_label = pygame_gui.elements.UILabel(
        relative_rect=pygame.Rect((Constants.MAIN_WIN_WIDTH - 300) // 2, 240, 300, 30 ),
        text=f"Mapa: {maps.get_available_maps()[0]}", manager=manager
    )

    pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((Constants.MAIN_WIN_WIDTH - 150) // 2, 300, 150, 40 ),
        text="Powrót", manager=manager
    )
    
    pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((Constants.MAIN_WIN_WIDTH - 150) // 2, 350, 150, 40), 
        text="Uruchom", manager=manager
    )
    
    return map_label


def create_settings_menu(manager: pygame_gui.UIManager) -> None:
    pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((Constants.MAIN_WIN_WIDTH - 150) // 2, 300, 150, 40 ),
        text="Powrót", manager=manager
    )
    
def create_pause_menu(manager: pygame_gui.UIManager) -> tuple[pygame_elements.UIButton, pygame_elements.UIButton]:
    panel_width = 300
    panel_height = 200
    pygame.Rect(
        (Constants.MAIN_WIN_WIDTH - panel_width) // 2,
        (Constants.MAIN_WIN_HEIGHT - panel_height) // 2,
        panel_width,
        panel_height
    )
    
    
    resume_button = pygame_elements.UIButton(
        relative_rect=pygame.Rect((Constants.MAIN_WIN_WIDTH - 150) // 2, (Constants.MAIN_WIN_HEIGHT - 60) // 2, 150, 40),
        text='Wznów', manager=manager
    )
    
    main_menu_button = pygame_elements.UIButton(
        relative_rect=pygame.Rect((Constants.MAIN_WIN_WIDTH - 150) // 2, (Constants.MAIN_WIN_HEIGHT + 60) // 2, 150, 40),
        text='Menu Główne', manager=manager
    )
    
    return resume_button, main_menu_button

def create_actions_menu(manager: pygame_gui.UIManager, track_element : TrackElement) -> List[pygame_gui.elements.UIButton]:
    font = pygame.font.Font(pygame.font.get_default_font(),)
    panel_width = sum([font.size(action_name)[0] + 5 for action_name in track_element.actions.keys()]) + 10 
    panel_height = 40
    
    panel_rect = pygame.Rect(((Constants.MAIN_WIN_WIDTH - panel_width) // 2, 50), 
                             (panel_width, panel_height))

    menu_panel = pygame_gui.elements.UIPanel(
        relative_rect=panel_rect,
        manager=manager,
        starting_height=10
    )

    buttons = []
    x_offset = 5
    for action_name in track_element.actions.keys():
        width = font.size(action_name)[0] + 5
        button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(x_offset, 5, width, 30),
            text=action_name,
            manager=manager,
            container=menu_panel,
            tool_tip_text=f"Execute {action_name}"
        )
        
        button.user_data = {"object": track_element, "action": action_name}
        buttons.append(button)
        x_offset += width
    
    return menu_panel, buttons