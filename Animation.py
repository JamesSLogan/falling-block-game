# "animation" = Text object that gets smaller over time
#
# 'update' function returns False to user when the object can be deleted
import pygame
from pygame.locals import *

from Settings import *
from Text     import Text

updates_per_second = 12
frames_between_updates = fps / updates_per_second
time_between_updates = int(1000/fps) * frames_between_updates

class Animation(pygame.sprite.Sprite):
    def __init__(self, data, clock, screen):
        self.data  = data
        self.clock = clock

        self.font_size_delta = 16
        self.time_since_last_update = 0
        self.newSprite()
        self.update(screen)

    def newSprite(self):
        self.time_since_last_update = 0
        self.sprite = Text((well_maxX - well_minX)/2 + well_minX,
                           (well_maxY - well_minY)/2 - well_minY, # above center
                           str(self.data), size_delta=self.font_size_delta,
                           color=animation_color)

        # Text won't set the surface if the font is too small
        if not self.sprite.surf:
            return False

        return True

    # Needs to be called every frame
    # Returns true if it should be kept alive
    def update(self, screen):
        self.time_since_last_update += self.clock.get_time()
        screen.blit(self.sprite.surf, self.sprite.rect)
        if self.time_since_last_update >= time_between_updates:
            self.font_size_delta -= 2
            self.time_since_last_update = 0
            return self.newSprite()
        return True
