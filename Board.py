# constructor(file) A Board with the description board is created
# attach(user, callback,
# turncb)
# User attaches to an existing board. Board events are sent to
# callback function
# detach(user) User detaches from the board. If game is started, all properties
# and money is returned as initialized
# ready(user) The attached user mark himself/herself as ready. When the all
# attached users mark the game ready, game starts.
# turn(user, command) When users turn, user gives the command/choice for his/her
# turn
# getuserstate(user) Generate a report for each user, money and properties with
# their levels
# getboardstate() Generates


# { cells: [{ type: "start"},
# { type: "property", name: 'bostancı', cell: 2, color: 'red',
# price:120, rents: [50,150,400,600,900]},
# { type: "teleport"}, {type: "tax"}, {type: "jail},...]
# upgrade: 50, teleport: 100, jailbail: 100,
# tax: 30, lottery: 200, startup: 1500,
# chances: [{type: "jump"},...}]
# }

import json
from Cell import Cell


class Board:
    def __init__(self, file):
        self.users = {}
        self.dice = None
        self.cells = []
        self.callbacks = {}
        with open(file) as f:
            data = json.load(f)
            # get both cell and index
            for index, cell in enumerate(data['cells']):
                self.cells.append(Cell(cell, index))
            self.upgrade = data['upgrade']
            self.teleport = data['teleport']
            self.jailbail = data['jailbail']
            self.tax = data['tax']
            self.lottery = data['lottery']
            self.startup = data['startup']
            # for card in data['chances']:

    def get_user_count(self):
        return len(list(self.users.keys()))

    def attach(self, user, callback, turncb):
        self.users[len(list(self.users.keys()))] = user
        self.callbacks[len(list(self.users.keys()))] = callback
        callback(self)
        pass

    def detach(self, user):
        pass

    def getuserstate(self, user):
        pass
        # return self.users[user.id]

    def getboardstate(self):
        pass

    def ready(self, user):
        pass

    def turn(self, user, command):
        pass

    def upgrade(self, property_index: int):
        if self.cells[property_index].level != 4:
            self.cells[property_index].level += 1

    def downgrade(self, property_index: int):
        if self.cells[property_index].level != 0:
            self.cells[property_index].level -= 1

    def color_upgrade(self, color: str):
        for prop in filter(lambda x: x.color == color and x.level != 4, self.cells):
            prop.level += 1

    def color_downgrade(self, color: str):
        for prop in filter(lambda x: x.color == color and x.level != 0, self.cells):
            prop.level -= 1

    def gotoJail(self, user):
        #TODO: Make user position jail and set boolean value inJail true
        pass

    def jailFree(self, user):
        #TODO: Make boolean value hasJail true.
        pass

    def __str__(self):
        return f'{self.cells} {self.upgrade} {self.teleport} {self.jailbail} {self.tax} {self.lottery} {self.startup}'