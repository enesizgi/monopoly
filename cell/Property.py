from typing import List


import sys
sys.path.append('..')
# import cell class
from .Cell import Cell
from User import User


class Property(Cell):

    def __init__(self, location: int, name: str, color: str, price: int, rents: List[int], cell_type):
        super().__init__(location, cell_type)
        self.name = name
        self.color = color
        self.price = price
        self.rents = rents
        self.level = 0
        self.owner_id = -1

    def buyProperty(self, user: User):
        user.budget -= self.price
        self.owner_id = user.id
        user.properties.append(self)

    def upgrade(self, fee=0, user: User = None):
        if user:
            user.budget -= fee

        if self.level < 5:
            self.level += 1

    def downgrade(self):
        if self.level > 0:
            self.level -= 1

    def payRent(self, owner: User, resident: User):

        if owner.inJail:
            return
        rent = self.rents[self.level]
        resident.budget -= rent
        owner.budget += rent

        print(f'{resident.username} paid {rent} to {owner.username} for {self.name}')


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


