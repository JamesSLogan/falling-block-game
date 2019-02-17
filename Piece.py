#
# A Piece is a collection of Blocks.
#
# Rotations are based off of this link:
# https://vignette.wikia.nocookie.net/tetrisconcept/images/3/3d/SRS-pieces.png
#
import random

import pygame
from pygame.locals import *

from Settings import *
from Block import Block

#
# 'coords': (x,y) coordinates of how the pieces should look when they start to
#           drop. Order is important because it will affect rotation.
# 'color' : piece's color
# 'rotate': hard-coded rotation deltas. Let's say each piece has 4 rotation
#           states, 0-3. The first entry in this field refers to the 0->1 and
#           1->0 transition. 1 is 1->2...etc.
#
piece_data = {
    ####
    'i' : {
        'coords' : ((0,0), (1,0), (2,0), (3,0)),
        'color'  : (0, 255, 255),
        'rotate' : [ ((2,-1), (1,0), (0,1), (-1,2)),
                     ((1,2),  (0,1), (-1,0), (-2,-1)),
                     ((-2,1), (-1,0), (0,-1), (1,-2)),
                     ((-1,-2), (0,-1), (1,0), (2,1)),
                   ]
    },

    ##
    ##
    'o' : {
        'coords' : ((0,0), (0,1), (1,0), (1,1)),
        'color'  : (255, 255, 0),
        'rotate' : []
    },

    #
    ###
    'j' : {
        'coords' : ((0,0), (0,1), (1,1), (2,1)),
        'color'  : (0, 0, 255),
        'rotate' : [ ((2,0),  (1,-1),  (0,0), (-1,1)),
                     ((0,2),  (1,1),   (0,0), (-1,-1)),
                     ((-2,0), (-1,1),  (0,0), (1,-1)),
                     ((0,-2), (-1,-1), (0,0), (1,1)),
                   ]
    },

      #
    ###
    'l' : {
        'coords' : ((2,0), (2,1), (1,1), (0,1)),
        'color'  : (255, 160, 0),
        'rotate' : [ ((0,2),  (-1,1),  (0,0), (1,-1)),
                     ((-2,0), (-1,-1), (0,0), (1,1)),
                     ((0,-2), (1,-1),  (0,0), (-1,1)),
                     ((2,0),  (1,1),   (0,0), (-1,-1)),
                   ]
    },

     #
    ###
    't' : {
        'coords' : ((1,0), (0,1), (1,1), (2,1)),
        'color'  : (255, 0, 255),
        'rotate' : [ ((1,1),   (1,-1),  (0,0), (-1,1)),
                     ((-1,1),  (1,1),   (0,0), (-1,-1)),
                     ((-1,-1), (-1,1),  (0,0), (1,-1)),
                     ((1,-1),  (-1,-1), (0,0), (1,1)),
                   ]
    },

     ##
    ##
    's' : {
        'coords' : ((1,0), (2,0), (0,1), (1,1)),
        'color'  : (0, 255, 0),
        'rotate' : [ ((1,1),   (0,2),  (1,-1),  (0,0)),
                     ((-1,1),  (-2,0), (1,1),   (0,0)),
                     ((-1,-1), (0,-2), (-1,1),  (0,0)),
                     ((1,-1),  (2,0),  (-1,-1), (0,0)),
                   ]
    },

    ##
     ##
    'z' : {
        'coords' : ((0,0), (1,0), (1,1), (2,1)),
        'color'  : (255, 0, 0),
        'rotate' : [ ((2,0),  (1,1),   (0,0), (-1,1)),
                     ((0,2),  (-1,1),  (0,0), (-1,-1)),
                     ((-2,0), (-1,-1), (0,0), (1,-1)),
                     ((0,-2), (1,-1),  (0,0), (1,1)),
                   ]
    },
}

class Piece(object):

    def __init__(self, clock, x_coord=None, y_coord=None, piece=None,
                 name=None):
        self.clock    = clock
        self.blocks   = []
        self.elapsed  = 0
        self.rotation = 0

        # Shadow pieces are based off an existing Piece
        if piece:
            self.name = piece.name
            self.coords = piece.coords
            color = shadow_color

            for (x,y) in self.coords:
                self.blocks.append(Block(x, y, color))
            self.moveToMiddleOfWell()

        # Normal pieces: pick a random one from the list and initialize its
        # blocks
        elif x_coord is None:

            if name:
                self.name = name
            else:
                self.name = random.choice(list(piece_data.keys()))
            self.coords = piece_data[self.name]['coords']
            color  = piece_data[self.name]['color']

            for (x,y) in self.coords:
                self.blocks.append(Block(x, y, color))
            self.moveToMiddleOfWell()

        # Invisible pieces: x and y coordinates are relative to the well. That
        # is, the top left box of the well is (0,0) and the bottom right is
        # generally 10,20. Note that border cells will be negative and/or
        # greated than the well's width/length.
        else:
            self.blocks.append(Block(x_coord, y_coord, None))

    def getSprites(self):
        return self.blocks

    def getRects(self): # for debugging only
        return ', '.join([str(block.rect) for block in self.blocks])

    def getGravity(self):
        return self.gravity

    def remove(self, block):
        block.kill() # this removes us from any sprite groups in the main file
        self.blocks.remove(block)

    # 'gravity' is how many cells to move a piece by each frame. If it's a
    # decimal values we will set gravity to 1 and increase the wait time
    # between drops.
    def setGravity(self, gravity=20):
        gravity = min(gravity, 20)

        if gravity >= 1:
            self.drop_wait = 1000/60 # 1 frame at 60 fps
        else:
            self.drop_wait = ((1000/gravity) / 60)
            gravity = 1

        self.gravity   = gravity
        self.drop_wait = int(self.drop_wait)

    # Move down if enough time has elapsed.
    def handleGravity(self, revertFunc):
        self.elapsed += self.clock.get_time()
        if self.elapsed > self.drop_wait:
            self.elapsed = 0
            for i in range(self.gravity):
                self.move(hard_drop_key)
                if revertFunc(self):
                    self.move(cheat_key)
                    return True
        return False

    # Move our blocks down if they're colliding with the given sheet.
    def downIfCollide(self, sheet):
        if not sheet:
            return

        for block in self.blocks:
            if pygame.sprite.collide_rect(sheet, block):
                block.move(hard_drop_key)

    def dispatch(self, key):
        if key in [cheat_key, hard_drop_key, soft_drop_key, left_key, right_key]:
            self.move(key)
        elif key in [cw_key, ccw_key]:
            self.rotate(key)

    # Move in a cardinal direction.
    def move(self, key): #, factor=None):
        for block in self.blocks:
            block.move(key) #, factor)

    def moveToMiddleOfWell(self):
        xOff = Piece.getMiddleOffset(self.coords)
        for i, block in enumerate(self.blocks):
            block.moveToMiddleOfWell(self.coords[i][0], self.coords[i][1], xOff)

    # (top of well)
    def moveToTop(self):
        # reset piece's rotation or coords will be off
        count = 0
        while self.rotation:
            self.rotate(cw_key)
            count += 1

        for i, block in enumerate(self.blocks):
            block.moveToTop(self.coords[i][1])

        # Rotate back
        for unused in range(count):
            self.rotate(ccw_key)

    def moveToHold(self):
        # reset piece's rotation so that we end up in the right place
        while self.rotation:
            self.rotate(cw_key)

        (xOff, yOff) = Piece.getHoldOffset(self.coords)
        for i, block in enumerate(self.blocks):
            block.moveToHold(self.coords[i][0], self.coords[i][1], xOff, yOff)

    # Move to area to the right of the well where upcoming pieces are stored
    def moveToNext(self, y):
        (xOff, yOff) = Piece.getNextOffset(self.coords, y)
        for i, block in enumerate(self.blocks):
            block.moveToNext(self.coords[i][0], self.coords[i][1], xOff, yOff)

    ###########################################################################
    #                                 ROTATION                                #
    ###########################################################################

    def incRotation(self):
        self.rotation = 0 if self.rotation == 3 else self.rotation+1
    def decRotation(self):
        self.rotation = 3 if self.rotation == 0 else self.rotation-1

    # Rotate piece
    def rotate(self, key):
        if not piece_data[self.name]['rotate']:
            return

        if key == cw_key:
            deltas = piece_data[self.name]['rotate'][self.rotation]
            self.incRotation()
        elif key == ccw_key:
            self.incRotation() # trust the process
            deltas = piece_data[self.name]['rotate'][self.rotation]
            self.decRotation()
            self.decRotation()

        for i, (x, y) in enumerate(deltas):
            self.blocks[i].adjust(x,y)

    ###########################################################################
    #                                  MISC                                   #
    ###########################################################################

    # Compute the offset (unit is block_size) that a piece needs to be centered
    # in a 6x4 box. This is one of the few times a piece won't necessarily be
    # on exactly on a grid.
    @staticmethod
    def getHoldOffset(coords):
        maxX = max(coords, key=lambda a:a[0])[0]
        maxY = max(coords, key=lambda a:a[1])[1]
        return (2.5 - maxX/2, 1.5 - maxY/2)

    # Compute the offset (unit is block_size) a piece needs to be centered at
    # the top of the well. There won't be any y offset since it's at the top.
    @staticmethod
    def getMiddleOffset(coords):
        maxX = max(coords, key=lambda a:a[0])[0]
        return int(well_width/2) - int((maxX+1)/2)

    # Compute the offset that a piece needs to be centered in the upcoming
    # pieces box. Since there are multiple pieces in the box we get passed
    # a y coordinate corresponding to our number in the box.
    def getNextOffset(coords, y):
        maxX = max(coords, key=lambda a:a[0])[0]
        maxY = max(coords, key=lambda a:a[1])[1]
        return (max_piece_width/2 - maxX/2, 1 - maxY/2 + y*blocks_between_next)
