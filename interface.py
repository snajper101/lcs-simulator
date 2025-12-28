import pygame
import pygame_gui
import pygame_gui.elements as pygame_elements
from constants import Constants
import maps

def create_main_menu( manager: pygame_gui.UIManager ) -> tuple[pygame_elements.UIButton, pygame_elements.UIButton, pygame_elements.UIButton]:
    #Play button
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

def create_maps_menu( manager: pygame_gui.UIManager ) -> pygame_elements.UIButton:
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


def create_settings_menu( manager: pygame_gui.UIManager ) -> None:
    pygame_gui.elements.UIButton(
        relative_rect=pygame.Rect((Constants.MAIN_WIN_WIDTH - 150) // 2, 300, 150, 40 ),
        text="Powrót", manager=manager
    )
    
def create_pause_menu(manager: pygame_gui.UIManager) -> tuple[pygame_elements.UIButton, pygame_elements.UIButton]:
    panel_width = 300
    panel_height = 200
    panel_rect = pygame.Rect(
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