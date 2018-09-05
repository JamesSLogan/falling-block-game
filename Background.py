import pygame
from pygame.locals import *

from Settings import *

class Background(pygame.sprite.Sprite):
    def __init__(self):
        self.surf = pygame.Surface((screen_width, screen_length))
        self.surf.fill(background_color)
        self.rect = self.surf.get_rect()

        pix = pygame.PixelArray(self.surf)

        # Set up holding area
        pix[hold_minX, hold_minY:hold_maxY] = pygame.Color(grid_color)
        pix[hold_maxX, hold_minY:hold_maxY] = pygame.Color(grid_color)
        pix[hold_minX:hold_maxX, hold_minY] = pygame.Color(grid_color)
        pix[hold_minX:hold_maxX, hold_maxY] = pygame.Color(grid_color)

        # Set up well by drawing vertical and horizonal lines to make a grid.
        for x in range(well_minX, well_maxX+block_size):
            if not (x-well_minX) % block_size:
                pix[x, well_minY:well_maxY] = pygame.Color(grid_color)

        for y in range(well_minY, well_maxY+block_size):
            if not (y-well_minY) % block_size:
                try:
                    pix[well_minX:well_maxX, y] = pygame.Color(grid_color)
                except:
                    pass

        # Set up "next piece" area
        pix[next_minX, next_minY:next_maxY] = pygame.Color(grid_color)
        pix[next_maxX, next_minY:next_maxY] = pygame.Color(grid_color)

        for i in range(num_next_pieces+1):
            pix[next_minX:next_maxX, next_minY+blocks_between_next*block_size*i] = pygame.Color(grid_color)

        pix.close()
