import pygame
import pygame_gui
import pygame_gui.elements as pygame_elements

def create_main_menu( manager: pygame_gui.UIManager ) -> None:
    #Play button
    pygame_elements.UIButton(relative_rect=pygame.Rect(0, 0, 100, 20),
          text='Hello', manager=manager,
          container=ui_window,
          anchors={'center': 'center'})
