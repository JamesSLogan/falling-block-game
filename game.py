#!/usr/bin/env python3
#
# firefox /usr/lib64/python3.4/site-packages/pygame/docs/ref/key.html
import sys
import time
import datetime
import random

import pygame
from pygame.locals import *

pygame.init()

import Level
import Sheet
import Scoring
from Piece        import Piece
from PieceManager import PieceManager
from Sheet        import Sheet
from Text         import Text
from Background   import Background
from Settings     import *

###############################################################################
#                                    GLOBALS                                  #
###############################################################################

clock      = pygame.time.Clock()
screen     = pygame.display.set_mode((screen_width, screen_length))
background = Background()
manager    = PieceManager(clock)

# Global sprite lists
all_drawable    = pygame.sprite.Group() # all drawable sprites except shadow
piece_sprites   = pygame.sprite.Group() # drawable sprites MINUS falling piece
falling_sprites = pygame.sprite.Group() # sprites related to falling piece
shadow_sprites  = pygame.sprite.Group() # falling piece's shadow

border       = pygame.sprite.Group() # outside of the well
border_U     = pygame.sprite.Group() # all of border minus the top
border_l     = pygame.sprite.Group() # left side of border
border_r     = pygame.sprite.Group() # right side of border
well         = pygame.sprite.Group() # whole well
well_rows    = [pygame.sprite.Group() for i in range(well_length)] # see below
well_sheets  = []                                                  # see below

# List of all Piece objects. Stored piece does not count (see 'hold()')
pieces = []

falling_piece = None
shadow_piece  = None

opposite = {
    left_key  : right_key,
    right_key : left_key,
    cw_key    : ccw_key,
    ccw_key   : cw_key,
}

down_keys      = [soft_drop_key, hard_drop_key, hard_drop_delay_key]
hard_drop_keys = [hard_drop_key, hard_drop_delay_key]
hard_drop_no_wait_keys = [hard_drop_key]

left_right_keys = [left_key, right_key]
rotate_keys     = [cw_key, ccw_key]

def groupcollide(left, right):
    return pygame.sprite.groupcollide(left, right, False, False)
anycollide = pygame.sprite.spritecollideany

last_stored = None

# Create extra variable just for code readability
level_enabled = False
if display_level:
    level_enabled = True

# Swaps falling & stored pieces. Kind of - it just returns them in reverse
# if the swap was successful.
def hold(falling, stored, gravity):
    global last_stored

    # Don't allow user to swap continuously
    if falling == last_stored:
        return falling, stored

    resetShadow(stored)

    falling_sprites.remove(falling.getSprites())
    pieces.remove(falling)
    if stored is None:
        stored = newPiece(gravity)
    else:
        all_drawable.add(stored.getSprites())
        falling_sprites.add(stored.getSprites())
        pieces.append(stored)
        stored.setGravity(gravity) # make sure it's up to date

    last_stored = stored

    falling.moveToHold()
    stored.moveToMiddleOfWell()
    return stored, falling

# A piece is in a bad place if:
# 1. It overlaps with something it shouldn't:
#   a. Another piece
#   b. The border of the well (see note below).
#
# 2. It doesn't overlap with the main board.
#
# We don't check the top of 'border' because pieces can rotate there if the
# player is quick enough, and that's valid.
def needToRevert(piece):
    sprites = piece.getSprites()
    if groupcollide(sprites, piece_sprites) or \
       groupcollide(sprites, border_U     ) or not \
       groupcollide(sprites, well         ):
        return True
    return False

# This code used to be in two places so it was worth condensing it
def checkDownwardRevert(piece):
    if needToRevert(piece):
        for i in range(well_length):
            piece.move(cheat_key)
            if not needToRevert(piece):
                break
        else:
            time.sleep(5)
            msg  = 'FATAL: Could not undo downward movement:\n'
            msg += '(%s)' % str(piece.getRects())
            raise RuntimeError(msg)
        return True
    else:
        return False

def oob(piece):
    for sprite in piece.getSprites():
        if not anycollide(sprite, well):
            return True
    return False

# Returns True if a kick was successful. Should be called with the assumption
# that something is wrong.
def kick(piece):
    wallKick(piece)
    if not needToRevert(piece):
        return True
    floorKick(piece)
    if not needToRevert(piece):
        return True
    return False

# If the piece is in an illegal place let's try to move it left or right.
def wallKick(piece):
    # Move the piece up to this many times.
    tries = 2

    # Move the piece to the left if it hits the right border
    if groupcollide(piece.getSprites(), border_r):
        for count in range(1, tries+1):
            piece.move(left_key)
            if not needToRevert(piece):
                return

        for unused in range(count):
            piece.move(right_key)

    # Move the piece to the right if it hits the left border
    elif groupcollide(piece.getSprites(), border_l):
        for count in range(1, tries+1):
            piece.move(right_key)
            if not needToRevert(piece):
                return

        for unused in range(count):
            piece.move(left_key)

# If the piece is in an illegal place let's try to move it up a block or two
def floorKick(piece):
    tries = 2
    if groupcollide(piece.getSprites(), piece_sprites) or \
       groupcollide(piece.getSprites(), well_rows[-1]):
        for count in range(1, tries+1):
            piece.move(cheat_key)
            if not needToRevert(piece):
                return

        for unused in range(count):
            piece.move(hard_drop_key)

# Checks two Pieces and returns True if the left is above the right. It assumes
# they're both the same shape.
def leftAboveRight(left, right):
    for well_row in well_rows:
        left_collide  = len(groupcollide(left.getSprites(), well_row))
        right_collide = len(groupcollide(right.getSprites(), well_row))
        if left_collide > right_collide:
            return True
        elif left_collide < right_collide:
            return False
    return False

# Create new piece and its shadow.
def newPiece(gravity):

    # Create new piece and save the one that just entered the upcoming zone.
    piece, new = manager.next(gravity)
    all_drawable.add(new.getSprites())

    # Set up new piece stuffs
    piece.moveToMiddleOfWell()
    falling_sprites.add(piece.getSprites())
    pieces.append(piece)

    # Check for game over
    if groupcollide(falling_sprites, piece_sprites):
        gameOver()

    newShadow(piece)

    return piece

# Create new shadow and move it down as far as possible.
def newShadow(piece):
    global shadow_piece

    shadow = Piece(clock, piece=piece)
    shadow_sprites.add(shadow.getSprites())
    shadowMove(shadow, hard_drop_key)
    shadow_piece = shadow

# Clears out shadow globals. Will populate them with optional parameter.
def resetShadow(restore_me=None):
    global shadow_piece
    global shadow_sprites

    shadow_piece = None

    for s in shadow_sprites:
        s.kill()
    shadow_sprites = pygame.sprite.Group()

    if restore_me:
        newShadow(restore_me)

# Move piece to the top of the well and all the way down until it hits the
# bottom or another piece.
def topAndDrop(piece):
    piece.moveToTop()
    for i in range(well_length):
        piece.move(hard_drop_key)
        if groupcollide(piece.getSprites(), piece_sprites) or \
           groupcollide(piece.getSprites(), well_rows[-1]):
            break
    else:
        time.sleep(2)
        raise RuntimeError('FATAL: Could not move piece up and down.')

    if groupcollide(piece.getSprites(), piece_sprites):
        piece.move(cheat_key) # have to move up 1 in this case


#
# Shadows need their own special movement for a few different reasons:
# 1. They need to be moved up and down on many left/right movements.
# 2. Their collision detection is different since a move is valid even if the
#    shadow collides with a piece
#
# Returns True if the move was successful
#
def shadowMove(shadow, key):
    if not shadow:
        return

    # It may look like repeated code but DON'T change it
    if key in left_right_keys:
        shadow.dispatch(key)
        if oob(shadow):
            shadow.dispatch(opposite[key])
            topAndDrop(shadow)
            return False

        topAndDrop(shadow)
        if leftAboveRight(shadow, falling_piece):
            shadow.dispatch(opposite[key])
            topAndDrop(shadow)
            return False

    elif key in rotate_keys:
        shadow.moveToTop()
        shadow.dispatch(key)
        if needToRevert(shadow) and not kick(shadow):
            shadow.dispatch(opposite[key])
            topAndDrop(shadow)
            return False

    topAndDrop(shadow)
    return True

# not exactly general-purpose
def timeObj(secs, msecs):
    ret = datetime.timedelta(seconds=secs, milliseconds=msecs)
    return ret, str(ret)[3:10]

def createText(x, y, base=''):
    ret = Text(x, y, str(base))
    all_drawable.add(ret)
    return ret

def updateText(text, msg):
    if text:
        text.update(str(msg))

# asdf
def updateScreen():
    screen.blit(background.surf, (0,0))

    # Falling piece can collide with its shadow so let's print the shadow first
    # so that it gets overwritten by the piece.
    for sprite in shadow_sprites:
        screen.blit(sprite.surf, sprite.rect)

    for sprite in all_drawable:
        screen.blit(sprite.surf, sprite.rect)

    pygame.display.flip()

def gameOver():
    updateScreen()
    print('GAME OVER')
    time.sleep(1)
    sys.exit(0)

def main():
    global falling_piece
    global shadow_piece
    global falling_sprites

    running = True

    new_piece_pending         = False
    new_piece_pending_elapsed = 0 # ms

    #
    # Text displays
    #
    level      = Level.startLevel()
    level_surf = None

    total_elapsed = 0
    zero_time     = datetime.timedelta(seconds=0)
    time_surf  = None

    points     = 0
    point_surf = None

    if display_level:
        lines = Level.lines(level)
    else:
        lines = start_lines # from Settings
    lines_surf = None

    if display_level:
        level_surf = createText(level_x, level_y, 'Level: ')
        updateText(level_surf, level)
    if display_time:
        time_surf = createText(time_x, time_y)
        updateText(time_surf, timeObj(time_limit, 0)[1])
    if display_points:
        point_surf = createText(points_x, points_y, 'Points: ')
        updateText(point_surf, points)
    if display_lines:
        lines_surf = createText(lines_x, lines_y, 'Remaining: ')
        updateText(lines_surf, lines)

    #
    # Delayed auto shift variables:
    #
    last_movement = 0 # tracks when last manual movement was
    das_triggered = False # tracks if DAS has been triggered

    #
    # The goal for hard drops is the piece to hit the bottom as fast as
    # possible. We want the user to be able to hold the hard drop button down
    # to continuously drop pieces too. BUT there needs to be a delay otherwise
    # they'll be forced to press the button for only one frame, otherwise
    # there's a good chance 2+ pieces will drop since we're running at 60 fps.
    #
    # SO, this is a delay that extends into the next piece.
    #
    hard_drop_repeat_wait         = 0
    hard_drop_repeat_wait_elapsed = 0

    #
    # Initialize invisible pieces that occupy the well. well_rows and
    # well_sheets are lists of sprite groups with one entry per row.
    #
    # well_rows: In order to detect when a row is complete we need 10 (width)
    #            surfaces per row to check when all of them are colliding with
    #            pieces on the screen.
    #
    # well_sheets: In order to move pieces down when a row is completed we
    #              need to be able to determine which blocks are *above* the
    #              row that is completed. Therefore these surfaces will stretch
    #              the width of the well and get longer and longer the farther
    #              down they are (stretching upward). These could be avoided
    #              if surfaces gave info about their position on the screen?
    #
    for y in range(0, well_length):
        # Initialize the sprites for each column
        for x in range(0, well_width):
            curr = Piece(clock, x_coord=x, y_coord=y).getSprites()
            well.add(curr)
            well_rows[y].add(curr)

        # Initialize the sheet.
        well_sheets.append(Sheet(y, well_width))

    # Initialize invisible pieces that line the outside of the well. In order:
    # top, right, bottom, left.
    border_coords  = [(x,-1)          for x in range(-1, well_width)]
    border_coords += [(well_width,y)  for y in range(-1, well_length)]
    border_coords += [(x,well_length) for x in range(well_width,  -1, -1)]
    border_coords += [(-1,y)          for y in range(well_length, -1, -1)]
    for (x,y) in border_coords:
        curr = Piece(clock, x_coord=x, y_coord=y)
        sprites = curr.getSprites()
        border.add(sprites)
        if not (y < 0 and x >= 0 and x < well_width):
            border_U.add(sprites) # shaped like a U
        if x < 0:
            border_l.add(sprites)
        if x == well_width:
            border_r.add(sprites)

    # Set up first piece
    all_drawable.add([piece.getSprites() for piece in manager.getPieces()])
    gravity = Level.gravity(level) # starts at 1 second per drop
    falling_piece = newPiece(gravity)

    saved_piece = None

    #
    # MAIN LOOP
    #
    while running:

        clock.tick(60)
        total_elapsed += clock.get_time()

        if display_time:
            if time_counts_up:
                time_obj, time_string = timeObj(0, total_elapsed)
            else:
                time_obj, time_string = timeObj(time_limit, -total_elapsed)
            updateText(time_surf, time_string)
            if time_obj <= zero_time:
                updateText(time_surf, zero_time)
                print(points)
                gameOver()

        last_movement += clock.get_time()

        reverted_downward_move = False

        new_piece_pending_period = Level.nppp(level)

        if new_piece_pending:
            new_piece_pending_elapsed += clock.get_time()

        if hard_drop_repeat_wait:
            hard_drop_repeat_wait_elapsed += clock.get_time()
            if hard_drop_repeat_wait_elapsed > 200:
                hard_drop_repeat_wait = False

        #######################################################################
        #                            KEY PRESSES                              #
        #######################################################################

        events = pygame.event.get()

        # Artificially add an arrow key to the events queue. Without this code,
        # holding a key down does nothing.
        if not events:
            keys = pygame.key.get_pressed()
            for key in hard_drop_key, left_key, right_key:
                if keys[key]:
                    if last_movement > 100 or das_triggered:
                        das_triggered = True
                        events.append(pygame.event.Event(KEYDOWN, {'key': key}))

        for event in events:
            if event.type == KEYDOWN:

                key = event.key

                # Quit
                if key in quit_keys:
                    running = False

                # Store piece and restart loop.
                elif key == hold_key:
                    falling_piece, saved_piece = hold(falling_piece,
                                                      saved_piece, gravity)

                    # NOTE: not sure if these are necessary but they could save
                    # the game from a few bugs.
                    new_piece_pending = False
                    das_triggered = False
                    last_movement = 0

                    updateScreen()
                    continue

                # Code related to user moving or rotating piece
                else:
                    last_movement = 0

                    # Code for downward movement - does not affect shadow.
                    if key in down_keys:
                        if key in hard_drop_keys:
                            if hard_drop_repeat_wait:
                                continue
                            lines_down = well_length
                        else:
                            lines_down = 1

                        successful_drops = 0
                        for i in range(lines_down):
                            falling_piece.move(hard_drop_key)
                            if needToRevert(falling_piece):
                                falling_piece.move(cheat_key)

                                # Override normal detection
                                if key in hard_drop_no_wait_keys:
                                    new_piece_pending = True
                                    new_piece_pending_period = 0
                                    hard_drop_repeat_wait = True
                                    hard_drop_repeat_wait_elapsed = 0
                                break
                            successful_drops += 1

                        if display_points:
                            points += Scoring.drop_points(successful_drops)
                            updateText(point_surf, points)

                    # Other movement
                    else:
                        # Let player move piece even around the bottom
                        #new_piece_pending = False

                        falling_piece.dispatch(key)
                        shadow_moved = shadowMove(shadow_piece, key)

                        # Try wall/floor kicks if a rotation was illegal.
                        if needToRevert(falling_piece) and key in rotate_keys:
                            kick(falling_piece)

                        # Revert movement if it was illegal and can't be done.
                        # shadowMove usually takes care of reverting itself but
                        # since the dection is different we need to double
                        # check here.
                        if needToRevert(falling_piece):
                            falling_piece.dispatch(opposite[key])
                            if shadow_moved:
                                shadow_moved = shadowMove(shadow_piece,
                                                          opposite[key])
                                if not shadow_moved:
                                    print('no revert = bad?')

                        # If we just moved the piece left/right and it's now
                        # over a gap, reset the new piece pending variables.
                        #if key in left_right_keys:
                        if True:
                            falling_piece.move(hard_drop_key)
                            if not needToRevert(falling_piece):
                                new_piece_pending = False
                            falling_piece.move(cheat_key)

            elif event.type == KEYUP:
                das_triggered = False
                if event.key in hard_drop_keys:
                    hard_drop_repeat_wait = False

            elif event.type == QUIT:
                running = False

        #######################################################################
        #                           PIECE MOVEMENT                            #
        #######################################################################

        # Auto movement
        if not new_piece_pending and falling_piece.handleGravity(needToRevert):
            #reverted_downward_move = checkDownwardRevert(falling_piece)
            reverted_downward_move = True


        # If the shadow and the falling piece overlap completely, we're at the
        # bottom so let's just kill off the shadow. This is really just because
        # shadow movement is buggy and this avoids some corner cases.
        if len(groupcollide(falling_sprites, shadow_sprites)) >= \
           len(falling_piece.getSprites()):
            resetShadow()


        # The piece can't move down farther if it just collided with another
        # piece or is currently colliding with the bottom row of invisible
        # blocks.
        if not new_piece_pending and (
            reverted_downward_move or
            groupcollide(falling_sprites, well_rows[-1])
        ):
            new_piece_pending         = True
            new_piece_pending_elapsed = 0

        # Piece is locked in. Check for row completion and eventually spawn a
        # new piece.
        if new_piece_pending and \
           new_piece_pending_elapsed >= new_piece_pending_period:

            new_piece_pending = False

            # Transfer falling_sprites to piece_sprites and reset variables
            # related to the falling piece.
            piece_sprites.add(falling_sprites)
            falling_sprites = pygame.sprite.Group()
            resetShadow()

            # Check all rows for completion.
            rows_completed = 0
            for i, row_sprites in enumerate(well_rows):
                sheet = well_sheets[i] # idx 0 will be None

                # 'collisions' will be a dict of Block objects that are in
                # 'piece_sprites'.
                collisions = groupcollide(piece_sprites, row_sprites)

                # Completed row!
                if len(collisions) == well_width:
                    rows_completed += 1

                    # Delete the row
                    for block in collisions:
                        for piece in pieces:
                            if block in piece.getSprites():
                                piece.remove(block)

                        # We don't need to keep empty Piece objects around.
                        if not piece.getSprites():
                            pieces.remove(piece)

                    # Move other pieces down.
                    for piece in pieces:
                        piece.downIfCollide(sheet)

            # Check for new level or game over, depending on the mode.
            if display_lines:
                lines -= rows_completed
                updateText(lines_surf, lines)

                if lines <= 0:
                    # New level
                    if level_enabled:
                        level += 1
                        lines, new_piece_pending_period, gravity = \
                                                    Level.updateLevel(level)
                        updateText(level_surf, level)
                        updateText(lines_surf, lines)
                    # User cleared all the lines
                    else:
                        updateText(lines_surf, 0)
                        print(timeObj(0, total_elapsed)[1])
                        gameOver()

            if display_points:
                points += Scoring.line_points(rows_completed)
                updateText(point_surf, points)

            falling_piece = newPiece(gravity)

        updateScreen()

main()
