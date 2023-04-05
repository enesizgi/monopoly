from typing import List

import sys
sys.path.append('..')

from .Cell import Cell
from .Property import Property
from User import User

import random


class ChanceCard(Cell):

    def __init__(self, location):
        super().__init__(location)
        self.card = None
        # define enum for chance cards

        self.chanceCards = ['Upgrade', 'Downgrade', 'Color Upgrade', 'Color Downgrade', 'Go to Jail', 'Jail Free Card',
                            "Lottery", "Tax"]

    def getChanceCard(self):
        self.card = random.choice(self.chanceCards)

    def applyChanceCard(self, props: List[Property] = None, user: User = None, board=None):
        if self.card == 'Upgrade':
            props[0].upgrade()
        elif self.card == 'Downgrade':
            props[0].downgrade()
        elif self.card == 'Color Upgrade':
            for prop in props:
                prop.upgrade()
        elif self.card == 'Color Downgrade':
            for prop in props:
                prop.downgrade()
        elif self.card == 'Go to Jail':
            user.location = board.jail_cell_index
            user.inJail = True
        elif self.card == 'Jail Free Card':
            user.jailFreeCard = True
        elif self.card == 'Lottery':
            user.budget += board.lottery
        elif self.card == 'Tax':
            user.budget -= board.tax
        self.card = None
