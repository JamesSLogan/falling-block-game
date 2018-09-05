#
# This should be implemented in the Block class but I decided to separate them
# as to not be misleading (a Sheet is always bigger than a Block).
#
# Anyway, a sheet is a single surface that spans above a given row to the top
# of the well.
#
import pygame
from pygame.locals import *

from Settings import *

class Sheet(pygame.sprite.Sprite):
    def __init__(self, y, width, color=(0,0,0)):
        super(Sheet, self).__init__()

        # There are no rows above the top row.
        if y < 1:
            self.surf = None
            return

        self.surf = pygame.Surface((width*block_size, y*block_size))
        self.surf.fill(color)
        self.rect = self.surf.get_rect(x=well_minX, y=well_minY)
