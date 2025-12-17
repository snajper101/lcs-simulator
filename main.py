import pygame
from game import main_loop
from constants import Constants
from profiles.data_manager import DataStore

if __name__ == "__main__":
    pygame.init()

    window_surface : pygame.surface = pygame.display.set_mode((Constants.MAIN_WIN_WIDTH, Constants.MAIN_WIN_HEIGHT))
    pygame.display.set_caption("Symulator LCS")

    dataStore : DataStore = DataStore()

    main_loop(window_surface)

    pygame.quit()