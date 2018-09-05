import pygame
from pygame.locals import *

from Settings import *

# font_size doesn't scale well currently, only tested with block_sizes of 20
# and 30
font_size = block_size + 10
font = pygame.font.SysFont('Arial', font_size)

class Text(pygame.sprite.Sprite):
    def __init__(self, x, y, base=''):
        super(Text, self).__init__()
        self.base = base
        self.surf = font.render(base, False, font_color)
        self.rect = self.surf.get_rect(x=x, y=y)

    def update(self, text):
        self.surf = font.render(self.base + text, False, font_color)
