#
# This class keeps track of the current pieces and works the rng of creating new
# pieces.
#
import random

from Settings import *
from Piece import Piece, piece_data

class PieceManager(object):
    def __init__(self, clock):
        self.pieces = []
        self.clock  = clock
        self.history = ['s', 's', 'z', 'z']

        for i in range(num_next_pieces):
            self.addNew()
        self.reposition()

    def getPieces(self):
        return self.pieces

    def addNew(self):
        self.pieces.append(Piece(self.clock, name=self.randPiece()))

    # Based on the TGM randomizer
    def randPiece(self):
        tries = 5
        # Try a certain number of times to pick a new piece.
        for unused in range(tries):
            curr = random.choice(list(piece_data.keys()))
            if curr not in self.history:
                break

        self.history.pop(0)
        self.history.append(curr)
        return curr

    def next(self, gravity):
        old = self.pieces.pop(0)
        self.addNew()
        self.reposition()
        if gravity:
            old.setGravity(gravity)
        return old, self.pieces[-1]

    def reposition(self):
        for y, piece in enumerate(self.pieces):
            piece.moveToNext(y)

    # "random generator" method - not in use
    def lazyBag(self):
        bag = []
        while len(bag) < bag_size:
            names = list(piece_data.keys())
            random.shuffle(names)
            for name in names:
                bag.append(name)
        self.bag = bag
