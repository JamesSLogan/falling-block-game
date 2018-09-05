from Settings import *

def line_points(lines, level=1):
    values = [0, 100, 400, 800, 1200]
    return level*values[lines]

def drop_points(lines):
    if drop_awards_points:
        # This should only happen for hard drop since soft will only be 1.
        # Max drop should be 20 so let's make it possible...only for 'i'
        # piece though.
        if lines > 1:
            return lines + 1
        else:
            return lines
    else:
        return 0
