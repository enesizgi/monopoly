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
        self.userTurn = []
        self.lastCommand = None
        with open(file) as f:
            data = json.load(f)
            self.salary = data['startup']
            self.upgrade = data['upgrade']
            self.teleport = data['teleport']
            self.jailbail = data['jailbail']
            self.tax = data['tax']
            self.lottery = data['lottery']
            # get both cell and index
            for cell, index in zip(data['cells'], range(len(data['cells']))):
                if cell['type'] == 'property':
                    self.cells.append(Property(index, cell['name'], cell['color'], cell['price'], cell['rents']))
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
        self.users[user.id] = user
        self.callbacks[user.id] = callback
        self.userTurn.append(user.id)
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
        if command['type'] == "pickProp":
            for i, cell in enumerate(self.cells):
                if cell.type == 'property':
                    print(f'{i}: {cell["name"]}')
            prop = int(input('Select possible property: (0,1,2...)'))
            self.cells[user.location].applyChanceCard([self.cells[prop]], user, self)
        elif command['type'] == 'pickColor':

            user_colors = set()
            for prop in user.properties:
                user_colors.add(prop.color)

            for i, color in enumerate(user_colors):
                print(f'{i}: {color}')

            prop = int(input('Select possible color to upgrade: (0,1,2...)'))
            color_props = self.getPropertiesByColor(list(user_colors)[prop])
            self.cells[user.location].applyChanceCard(color_props, user, self)
        elif command['type'] == "roll":
            dice = self.get_random_dice()
            user.move(dice, len(self.cells), self.salary)
        elif command['type'] == "buy":
            self.cells[user.location].buyProperty(user)
        elif command['type'] == "upgrade":
            command['property'].upgrade()
        elif command['type'] == "bail":
            if user.hasJailFreeCard:
                answer = input('Do you want to use your jail free card? (y/n)')
                if answer == 'y':
                    user.hasJailFreeCard = False
                    user.jailTurns = 0
                    user.inJail = False
            else:
                self.cells[user.location].pay_bail(user)
        elif command['type'] == "teleport":
            destination = command['destination']
            self.cells[user.location].teleport(user, destination)

        # call back for all users
        # turncb for next user
        self.lastCommand = command

    def getPropertiesByColor(self, color):
        return list(filter(lambda x: x.color == color, self.cells))

    def start(self):
        self.started = True
        while self.started:
            user = self.determine_next_user()
            possible_commands = []
            try:
                possible_commands = self.get_possible_commands(user)
            except Exception as e:
                print(e)
                break

            if len(possible_commands) != 0:
                selected_command = user.notifyTurn(possible_commands)

            self.turn(user, selected_command)
            self.lastCommand = selected_command

            for callback in self.callbacks.values():
                callback(self.getboardstate())

    def get_possible_commands(self, user):
        possible_commands = []

        if self.lastCommand is None or self.lastCommand['type'] != "roll" or self.lastCommand['type'] == "bail":
            possible_commands.append({'type': 'roll'})

        elif self.lastCommand['type'] == "roll":

            if self.cells[user.location].type == "property":
                if self.cells[user.location].owner_id == -1:
                    possible_commands.append({'type': 'buy'})
                elif self.cells[user.location].owner_id == user.id:
                    possible_commands.append({'type': 'upgrade'})
                else:
                    prop = self.cells[user.location]
                    prop.payRent(self.users[prop.owner_id], user)

                    if user.budget < 0:
                        self.started = False
                        raise Exception("User {} is bankrupt".format(user.id))


            elif self.cells[user.location].type == "teleport":
                possible_commands.append({'type': 'teleport'})
            elif self.cells[user.location].type == "chance":
                chance_cell = self.cells[user.location]
                chance_cell.getChanceCard()
                if chance_cell.card == 'Upgrade' or chance_cell.card == 'Downgrade':
                    possible_commands.append({'type': 'pickProp'})
                elif chance_cell.card == 'Color Upgrade' or chance_cell.card == 'Color Downgrade':
                    possible_commands.append({'type': 'pickColor'})
                else:
                    chance_cell.applyChanceCard(None, user, self)

                    if chance_cell.card == 'Tax':
                        if user.budget < 0:
                            self.started = False
                            raise Exception("User {} is bankrupt".format(user.id))
            elif user.inJail:
                if user.budget > self.jailbail or user.hasJailFreeCard:
                    possible_commands.append({'type': 'bail'})
                    user.jailTurns += 1
                else:
                    if user.jailTurns > 0:
                        user.jailTurns = 0
                        user.inJail = False
                    else:
                        user.jailTurns += 1

            elif self.cells[user.location].type == "gotojail":
                self.cells[user.location].goto_jail(user, user.location)
            elif self.cells[user.location].type == "tax":
                tax_cell = self.cells[user.location]
                tax_cell.pay_tax(user)

                if user.budget < 0:
                    self.started = False
                    raise Exception("User {} is bankrupt".format(user.id))

        return possible_commands

    def determine_next_user(self):

        if self.lastCommand is not None and self.lastCommand['type'] != "roll" and self.lastCommand['type'] != 'bail':
            last_user = self.userTurn.pop(0)
            self.userTurn.append(last_user)

        return self.users[self.userTurn[0]]

    def __str__(self):
        return f'{self.cells} {self.upgrade} {self.teleport} {self.jailbail} {self.tax} {self.lottery} {self.salary}'
