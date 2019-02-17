import pygame
from pygame.locals import *

from Settings import *

# font sizes don't scale well currently, only tested with block_sizes of 20
# and 30
font_size = block_size
#font = pygame.font.SysFont('Arial', font_size)

#animated_size = block_size
#animation_font = pygame.font.SysFont('Arial', animated_size)

class Text(pygame.sprite.Sprite):
    def __init__(self, x, y, base='', size_delta=0, color=font_color):
        super(Text, self).__init__()
        self.base  = base
        self.color = color
        self.surf  = None
        calc_size  = font_size + size_delta
        if (calc_size > 6):
            self.font = pygame.font.SysFont('Arial', calc_size)
            self.surf = self.font.render(base, False, self.color)
            self.rect = self.surf.get_rect(x=x, y=y)

    def update(self, text):
        self.surf = self.font.render(self.base + text, False, self.color)

    def move(self, x, y):
        self.rect.move_ip(x, y)
