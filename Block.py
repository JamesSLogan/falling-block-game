import pygame
from pygame.locals import *

from Settings import *

class Block(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        super(Block, self).__init__()
        self.surf = pygame.Surface((block_size, block_size))

        # Normal blocks
        if color:
            self.surf.fill(color)

            # Draw border
            pix = pygame.PixelArray(self.surf)
            lim = block_size-1
            pix[0,     0:lim] = pygame.Color(piece_grid_color)
            pix[lim,   0:lim] = pygame.Color(piece_grid_color)
            pix[0:lim, 0]     = pygame.Color(piece_grid_color)
            pix[0:lim, lim]   = pygame.Color(piece_grid_color)

        # Invisible blocks
        else:
            self.rect = self.surf.get_rect(x=well_minX + x*block_size,
                                           y=well_minY + y*block_size)
            self.surf.fill((255,0,255))

    # Move in place a certain direction
    def move(self, key):
        before = str(self.rect)
        if key == cheat_key: # hax m0de
            self.rect.move_ip(0, -block_size)
        if key == hard_drop_key or key == soft_drop_key:
            self.rect.move_ip(0, block_size)
        if key == left_key:
            self.rect.move_ip(-block_size, 0)
        if key == right_key:
            self.rect.move_ip(block_size, 0)
        #print('m: %s -> %s' % (before, self.rect))

    # Move in place a manual setting
    def adjust(self, x, y):
        before = str(self.rect)
        self.rect.move_ip(x*block_size, y*block_size)
        #print('a: %s -> %s' % (before, self.rect))

    # Move to top, middle of the well
    def moveToMiddleOfWell(self, x, y, xOffset):
        self.reset()
        self.rect.move_ip(well_minX + x*block_size + xOffset*block_size,
                          well_minY + y*block_size)

    # Move to top of well without modifying our x coordinate.
    def moveToTop(self, y):
        while self.rect.y > well_minY+y*block_size:
            self.move(cheat_key)

    # Move to holding area
    def moveToHold(self, x, y, xOffset, yOffset):
        self.reset()
        self.rect.move_ip(hold_minX + x*block_size + xOffset*block_size,
                          hold_minY + y*block_size + yOffset*block_size)

    def moveToNext(self, x, y, xOffset, yOffset):
        self.reset()
        self.rect.move_ip(next_minX + x*block_size + xOffset*block_size,
                          next_minY + y*block_size + yOffset*block_size)

    def reset(self):
        self.rect = self.surf.get_rect()
