import pygame
from game import main_loop
import constants
from data_manager import DataStore

if __name__ == "__main__":
    pygame.init()

    window_surface : pygame.surface = pygame.display.set_mode((constants.MAIN_WIN_WIDTH, constants.MAIN_WIN_HEIGHT))
    pygame.display.set_caption("Symulator LCS")

    dataStore : DataStore = DataStore()

    main_loop(window_surface)

    pygame.quit()