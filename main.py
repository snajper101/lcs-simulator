import pygame
from game import main_loop
import constants

if __name__ == "__main__":
    pygame.init()

    pygame.display.set_mode((constants.MAIN_WIN_WIDTH, constants.MAIN_WIN_HEIGHT))
    pygame.display.set_caption("Symulator LCS")

    main_loop()

    pygame.quit()