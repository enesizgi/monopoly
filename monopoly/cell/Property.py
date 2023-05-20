from typing import List


import sys
sys.path.append('..')
# import cell class
from .Cell import Cell
from ..User import User
# from User import User


class Property(Cell):

    """
    This class represents a property cell in the board.
    """

    def __init__(self, location: int, name: str, color: str, price: int, rents: List[int], cell_type):
        super().__init__(location, cell_type)
        self.name = name
        self.color = color
        self.price = price
        self.rents = rents
        self.level = 0
        self.owner_id = -1

    def buyProperty(self, user: User):
        """
        This method buys the property by setting the owner_id to the user id and deducting the price from the user budget.
        :param user: User object
        :return:
        """
        user.budget -= self.price
        self.owner_id = user.id
        user.properties.append(self)

    def upgrade(self, fee=0, user: User = None):
        """
        This method upgrades the property by increasing the level by 1.
        :param fee:
        :param user:
        :return:
        """

        # This check is for the case when the user is upgrading the property by paying the fee and not by using a chance card.
        if user:
            user.budget -= fee

        if self.level < 5:
            self.level += 1

    def downgrade(self):
        """
        This method downgrades the property by decreasing the level by 1.
        :return:
        """
        if self.level > 0:
            self.level -= 1

    def payRent(self, owner: User, resident: User):

        """
        This method pays the rent to the owner by deducting the rent from the resident budget and adding it to the owner budget.
        :param owner:
        :param resident:
        :return:
        """

        # If the owner is in jail, the rent is not paid.
        if owner.inJail:
            return
        rent = self.rents[self.level]
        resident.budget -= rent
        owner.budget += rent


    def __repr__(self):
        return self.name + " " + str(self.location)

    def getstate(self):
        return {
            'location': self.location,
            'name': self.name,
            'color': self.color,
            'price': self.price,
            'rents': self.rents,
            'level': self.level,
            'owner_id': self.owner_id,
            'type': 'Property'
        }


