from pygame.locals import *

###############################################################################
#                                     KEYS                                    #
###############################################################################

soft_drop_key = K_UP
hard_drop_key = K_DOWN
hard_drop_delay_key = K_e
left_key  = K_LEFT
right_key = K_RIGHT
cw_key    = K_f
ccw_key   = K_s
hold_key  = K_SPACE
cheat_key = K_POWER
quit_keys = [K_ESCAPE, K_q]

###############################################################################
#                                    MODES                                    #
###############################################################################

#mode = '2min'
time_limit = 120

mode = 'lines'
start_lines = 100

#mode = 'infinite'

display_level  = False
display_time   = False
display_points = False
display_lines  = False
time_counts_up = False
drop_awards_points = False

if mode == '2min':
    display_time   = True
    display_points = True

elif mode == 'lines':
    display_time   = True
    display_lines  = True
    time_counts_up = True

elif mode == 'infinite':
    display_level  = True
    display_lines  = True
    display_points = True
    drop_awards_points = True

else:
    raise RuntimeError('u wot')

###############################################################################
#                                SCREEN VARIABLES                             #
###############################################################################
#
# Change screen settings at your own risk, I haven't tested all the possible
# combinations...
#
well_width  = 10
well_length = 20
block_size  = 30
num_next_pieces = 3

between_padding = 50  # between objects on the screen

max_piece_width = 4

# Start of the screen: holding area at top left.
hold_minX = between_padding
hold_maxX = hold_minX + 6*block_size
hold_minY = between_padding
hold_maxY = hold_minY + 4*block_size

# Mode settings determine what to display on the left side of the screen.
# All of their x values are the same.
# We set all the y values to the same starting value and increase based on what
# needs to be displayed. Not all of these will be used.
level_x = time_x = points_x = lines_x = hold_minX
level_y = time_y = points_y = lines_y = hold_maxY + between_padding
if display_level:
    time_y   += between_padding
    points_y += between_padding
    lines_y  += between_padding
if display_time:
    points_y += between_padding
    lines_y  += between_padding
if display_points:
    lines_y  += between_padding

# We want a 10x20 grid with each cell being block_size.
well_minX = hold_maxX + between_padding
well_maxX = well_minX + block_size*well_width
well_minY = hold_minY
well_maxY = well_minY + block_size*well_length

# Max piece width is 4 so let's make it 5 wide
next_minX = well_maxX + between_padding
next_maxX = next_minX + 5*block_size
# Max piece length is 2 and we want 1 block space between each piece so that
# gets us 3*num_pieces.
blocks_between_next = 3
next_minY = hold_minY
next_maxY = next_minY + blocks_between_next*block_size*num_next_pieces

# Calculated screen variables
length_padding = 100 # just some extra space
outside_padding = 0
hold_padding    = 200 # extra space for "hold" section
next_padding    = 200 # extra space for "next pieces" section

screen_width  = hold_padding + between_padding + \
                well_width*block_size + between_padding + \
                next_padding + between_padding
screen_length = length_padding + well_length*block_size

###############################################################################
#                                   COLORS                                    #
###############################################################################
# Note that pygame.surface.fill and pyame.Color expect different forms of
# input.
black = (0,0,0)
white = (255,255,255)
shadow_color = (200,200,200)
font_color = (0,255,0)
animation_color = (255,0,0)
background_color = black
grid_color = 'green'
piece_grid_color = 'black'

###############################################################################
#                                   SCORING                                   #
###############################################################################

###############################################################################
#                                    MISC                                     #
###############################################################################

bag_size = 7 # piece manager unused rng

countdown_secs = 3 # 0 to disable

fps = 60 # I have not tried messing with this

# There are 2 hard drops. One will spawn a piece within the next frame, the
# other will wait so that you can move the piece for a certain amount of time.
# In infinite mode that time period is set, but otherwise you can set it to
# the milliseconds below.
hard_drop_wait = 300
