# TODO: turncb and callbacks
# TODO: Turn command with proper commands to be displayed
# TODO: Testing with threads

import json
from cell.Property import Property
from cell.Teleport import Teleport
from cell.Tax import Tax
from cell.Jail import Jail
from cell.ChanceCard import ChanceCard
from cell.Start import Start
from User import User
from cell.GotoJail import GotoJail
import random
import cmd


class Board(cmd.Cmd):
    def __init__(self, file):
        super().__init__()
        self.users = {}
        self.cells = []
        self.callbacks = {}
        self.started = False
        self.userTurn = []
        self.lastCommand = None
        # self.current_user = 0
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
                    self.cells.append(
                        Property(index, cell['name'], cell['color'], cell['price'], cell['rents'], cell['type']))
                elif cell['type'] == 'teleport':
                    self.cells.append(Teleport(index, data['teleport'], cell['type']))
                elif cell['type'] == 'tax':
                    self.cells.append(Tax(index, data['tax'], cell['type']))
                elif cell['type'] == 'jail':
                    self.cells.append(Jail(index, data['jailbail'], cell['type']))
                    self.jail_cell_index = index
                elif cell['type'] == 'chance':
                    self.cells.append(ChanceCard(index, cell['type']))
                elif cell['type'] == 'start':
                    self.cells.append(Start(index, data['startup'], cell['type']))
                elif cell['type'] == 'gotojail':
                    self.goto_jail_index = index
                    self.cells.append(GotoJail(index, cell['type']))

    def get_user_count(self):
        '''Returns the number of users in the game'''
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
        return user.get()

    def to_json(self, obj):
        return json.dumps(obj, sort_keys=True, indent=4)

    def getboardstate(self):

        return json.dumps({
            'users': [self.getuserstate(user) for user in self.users.values()],
            'cells': [cell.getstate() for cell in self.cells],
            'started': self.started,
            'userTurn': self.userTurn,
            'lastCommand': self.lastCommand,
            'salary': self.salary,
            'upgrade': self.upgrade,
            'teleport': self.teleport,
            'jailbail': self.jailbail,
            'tax': self.tax,
            'lottery': self.lottery,
        }, indent=4)

    def ready(self, user):
        user.ready = True
        if all(user.ready for user in self.users.values()):
            print('Game started')
            self.start()

    def get_random_dice(self):
        dice = random.randint(1, 6), random.randint(1, 6)
        print(f'You rolled {dice}!')
        return dice

    def turn(self, user, command):
        self.lastCommand = command

        if command['type'] == "roll":
            dice = self.get_random_dice()
            user.move(dice, len(self.cells), self.salary)
            name = getattr(self.cells[user.location], 'name', '')
            print(f'You have arrived {self.cells[user.location].type} {name}!')
            # return

        elif command['type'] == "bail":
            if user.hasJailFreeCard:
                answer = input('Do you want to use your jail free card? (y/n)')
                if answer == 'y':
                    user.hasJailFreeCard = False
                    user.jailTurns = 0
                    user.inJail = False
            else:
                self.cells[user.location].pay_bail(user)

            print(self.getuserstate(user))

            # return

        # self.current_user = (self.current_user + 1) % len(self.userTurn)

        elif command['type'] == "pickProp":
            for i, cell in enumerate(self.cells):
                if cell.type == 'property':
                    print(f'{i}: {cell["name"]}')
            prop = int(input('Select possible property: (0,1,2...)\n'))
            self.cells[user.location].applyChanceCard([self.cells[prop]], user, self)
        elif command['type'] == 'pickColor':

            user_colors = set()
            for prop in user.properties:
                user_colors.add(prop.color)

            if len(user_colors) != 0:
                for i, color in enumerate(user_colors):
                    print(f'{i}: {color}')

                prop = int(input('Select possible color to upgrade: (0,1,2...)\n'))
                color_props = self.getPropertiesByColor(list(user_colors)[prop])
                self.cells[user.location].applyChanceCard(color_props, user, self)

        elif command['type'] == "buy":
            self.cells[user.location].buyProperty(user)
            print(self.getuserstate(user))
        elif command['type'] == "upgrade":
            self.cells[user.location].upgrade(self.upgrade, user)
            print(self.getuserstate(user))

        elif command['type'] == "teleport":
            destination = input(f'Enter your destination between 0 and {len(self.cells) - 1}:\n')
            self.cells[user.location].teleport(user, destination)

        # call back for all users
        # turncb for next user

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
                return
            finally:
                if len(possible_commands) != 0:
                    selected_command = user.notifyTurn(possible_commands)
                    self.turn(user, selected_command)
                    self.lastCommand = selected_command
                else:
                    last_user = self.userTurn.pop(0)
                    self.userTurn.append(last_user)
                    self.lastCommand = None
                for callback in self.callbacks.values():
                    callback(self.getboardstate())

    def get_possible_commands(self, user):
        possible_commands = []

        if self.lastCommand is None or self.lastCommand['type'] != "roll" or self.lastCommand['type'] == "bail":
            possible_commands.append({'type': 'roll'})

        elif self.lastCommand['type'] == "roll":

            if self.cells[user.location].type == "property":
                if self.cells[user.location].owner_id == -1:
                    if user.budget > self.cells[user.location].price:
                        possible_commands.append({'type': 'buy'})
                        possible_commands.append({'type': 'skip'})
                elif self.cells[user.location].owner_id == user.id:
                    if user.budget > self.upgrade:
                        possible_commands.append({'type': 'upgrade'})
                        possible_commands.append({'type': 'skip'})
                else:
                    prop = self.cells[user.location]
                    prop.payRent(self.users[prop.owner_id], user)

                    if user.budget < 0:
                        self.started = False
                        raise Exception("User {} is bankrupt".format(user.id))


            elif self.cells[user.location].type == "teleport":
                if user.budget > self.teleport:
                    possible_commands.append({'type': 'teleport'})
                    possible_commands.append({'type': 'skip'})
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
                    if user.jailTurns > 1:
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
