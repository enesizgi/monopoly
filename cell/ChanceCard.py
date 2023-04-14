from typing import List
import json

import sys
sys.path.append('..')

from .Cell import Cell
from .Property import Property
from User import User

import random


class ChanceCard(Cell):
    
    """
    This class represents a chance card cell in the board.
    """

    def __init__(self, location, cell_type):
        super().__init__(location, cell_type)
        self.card = None
        # define enum for chance cards

        self.chanceCards = ['Upgrade', 'Downgrade', 'Color Upgrade', 'Color Downgrade', 'Go to Jail', 'Jail Free Card',
                            "Lottery", "Tax"]

    def getChanceCard(self):
        """
        This method returns a random chance card from the list of chance cards.
        :return: 
        """
        chance_card = random.choice(self.chanceCards)
        print(f'You picked this chance card: {chance_card}!\n')
        self.card = chance_card

    def applyChanceCard(self, props: List[Property] = None, user: User = None, board=None):
        
        """
        This method applies the chance card to the user.
        :param props: If the chance card is an upgrade or downgrade card, the properties are passed to this method.
        :param user: If the chance card is a jail card, the user is passed to this method.
        :param board: If the chance card is a lottery card, the board is passed to this method.
        :return: 
        """
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

    def to_json(self):
        return json.dumps({
            "location": self.location,
        })

    def getstate(self):
        return {
            "location": self.location,
            "type": "Chance",
        }
