# Manages various variables that speed up each level
from Settings import *

def startLevel():
    return 1

def updateLevel(level):
    return lines(level), nppp(level), gravity(level)

def lines(level):
    return 10

# new_piece_pending_period: probably has an official name somewhere
def nppp(level):
    ret = 950 - level*50
    return ret if ret > 0 else 0

def gravity(level):
    data = [.0166, .0208, .0277, .0416, .0833, .1666, .3333, .6666, 1, 2, 4, 8, 20]
    level = min(level, len(data)-1)
    ret = data[level]
    return ret if ret <= well_length else well_length
