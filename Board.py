# TODO: turncb and callbacks
# TODO: Turn command with proper commands to be displayed
# TODO: Testing with threads

import json
from cell.Cell import Cell
from cell.Property import Property
from cell.Teleport import Teleport
from cell.Tax import Tax
from cell.Jail import Jail
from cell.ChanceCard import ChanceCard
from cell.Start import Start
from User import User
from cell.GotoJail import GotoJail
import random


class Board:
    def __init__(self, file):
        self.users = {}
        self.cells = []
        self.callbacks = {}
        self.started = False
        with open(file) as f:
            data = json.load(f)
            self.salary = data['startup']
            self.upgrade = data['upgrade']
            self.teleport = data['teleport']
            self.jailbail = data['jailbail']
            self.tax = data['tax']
            self.lottery = data['lottery']
            # get both cell and index
            self.cells.append(Cell(None))
            for cell, index in zip(data['cells'], range(1, len(data['cells']) + 1)):
                if cell['type'] == 'property':
                    self.cells.append(Property(cell['cell'], cell['name'], cell['color'], cell['price'], cell['rents']))
                elif cell['type'] == 'teleport':
                    self.cells.append(Teleport(index, teleport_fee=data['teleport']))
                elif cell['type'] == 'tax':
                    self.cells.append(Tax(index, tax=data['tax']))
                elif cell['type'] == 'jail':
                    self.cells.append(Jail(index, jail_bail=data['jailbail']))
                    self.jail_cell_index = index
                elif cell['type'] == 'chance':
                    self.cells.append(ChanceCard(index))
                elif cell['type'] == 'start':
                    self.cells.append(Start(index, salary=data['startup']))
                elif cell['type'] == 'gotojail':
                    self.goto_jail_index = index
                    self.cells.append(GotoJail(index))

    def get_user_count(self):
        return len(list(self.users.keys()))

    def attach(self, user: User, callback, turncb):
        self.users[len(list(self.users.keys()))] = user
        self.callbacks[len(list(self.users.keys()))] = callback
        # callback(self)

        callback(self.getboardstate())
        # user.turncb = turncb

        # callback(Event)

    def detach(self, user):

        if self.started:
            # return money and properties
            for prop in user.properties:
                prop.owner = -1
                prop.level = 0

            user.ready = False
        self.users.pop(user.id)

    def getuserstate(self, user):
        return user.getState()

    def getboardstate(self):
        return {
            'cells': self.cells,
            'upgrade': self.upgrade,
            'teleport': self.teleport,
            'jailbail': self.jailbail,
            'tax': self.tax,
            'lottery': self.lottery,
            'startup': self.salary,
            'users': self.users
        }

    def ready(self, user):
        user.ready = True
        if all(user.ready for user in self.users.values()):
            self.start()

    def get_random_dice(self):
        return random.randint(1, 6), random.randint(1, 6)

    def turn(self, user, command):
        if command['type'] == "pick":
            self.cells[user.location].applyChanceCard(command['properties'], user, self)
        elif command['type'] == "roll":
            dice = self.get_random_dice()
            user.move(dice, len(self.cells), self.salary)
        elif command['type'] == "buy":
            command['property'].buyProperty(user)
        elif command['type'] == "upgrade":
            command['property'].upgrade()
        elif command['type'] == "bail":
            self.cells[user.location].pay_bail(user)
        elif command['type'] == "teleport":
            destination = command['destination']
            self.cells[user.location].teleport(user, destination)

        # call back for all users
        # turncb for next user
        pass

    def getPropertiesByColor(self, color):
        return list(filter(lambda x: x.color == color, self.cells))

    def start(self):
        self.started = True
        pass

    def __str__(self):
        return f'{self.cells} {self.upgrade} {self.teleport} {self.jailbail} {self.tax} {self.lottery} {self.salary}'
