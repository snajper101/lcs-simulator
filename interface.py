import pygame
import pygame_gui
import pygame_gui.elements as pygame_elements
import constants

def create_main_menu( manager: pygame_gui.UIManager ) -> tuple[pygame_elements.UIButton, pygame_elements.UIButton]:
    #Play button
    play_button = pygame_elements.UIButton(
        relative_rect=pygame.Rect((constants.MAIN_WIN_WIDTH - constants.BUTTON_WIDTH) // 2, (constants.MAIN_WIN_HEIGHT - constants.BUTTON_HEIGHT) // 2, 150, 40),
        text='Graj', manager=manager
    )
    
    settings_button = pygame_elements.UIButton(
        relative_rect=pygame.Rect((constants.MAIN_WIN_WIDTH - constants.BUTTON_WIDTH) // 2, (constants.MAIN_WIN_HEIGHT + constants.BUTTON_HEIGHT) // 2, 150, 40),
        text='Ustawienia', manager=manager
    )
    
    return ( play_button, settings_button )