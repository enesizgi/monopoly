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


# Main board class
class Board:
    def __init__(self, file):

        '''
            Constructor for the board class. Takes in a json file and parses it to create the board.
        :param file: .json file containing the board information
        '''

        self.users = {}  # holds all the users, used dictionary for easy access (key = user_id)
        self.cells = []  # holds all the cells
        self.callbacks = {}  # holds all the callbacks assigned to each user
        self.started = False  # boolean to check if the game has started, is used in main game loop
        self.userTurn = []
        self.lastCommand = None  # holds the last command that is executed
        self.turn_changed = False
        # self.current_user = 0
        with open(file) as f:
            data = json.load(f)
            self.salary = data['startup']
            self.upgrade = data['upgrade']
            self.teleport = data['teleport']
            self.jailbail = data['jailbail']
            self.tax = data['tax']
            self.lottery = data['lottery']

            # Based on the type of cell, creates the appropriate cell object and appends it to the cells list
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
        """Returns the number of users in the game"""
        return len(list(self.users.keys()))

    def attach(self, user: User, callback, turncb):

        """
        Attaches a user to the board. This is called when a user joins the game.
        :param user:
        :param callback:
        :param turncb:
        :return:
        """
        self.users[user.id] = user
        self.callbacks[user.id] = callback
        self.userTurn.append(user.id)

        callback(self.getboardstate())

    def detach(self, user):
        """
        Detaches a user from the board. This is called when a user leaves the game.
        :param user:
        :return:
        """

        # if the game has started, return the user's money and properties, and set the user's ready status to false
        if self.started:
            # return money and properties
            for prop in user.properties:
                prop.owner = -1
                prop.level = 0

            user.ready = False
            # self.started = False
        self.users.pop(user.id)

    def getuserstate(self, user):
        """
        Returns the state of the user by calling the user's get method
        :param user: User object
        :return: json string
        """
        return user.get()

    def getboardstate(self):
        """
        Returns the state of the board by calling the getstate method of each cell and user. Added indent=4 for
        readability
        :return: json string
        """

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
        """
        Sets the user's ready status to true and checks if all users are ready. If all users are ready, the game starts.
        :param user: User object
        :return:
        """
        user.ready = True
        if all(user.ready for user in self.users.values()):
            print('Game started')
            self.start()

    def get_random_dice(self):
        """
        Returns a random dice roll
        :return:
        """
        dice = random.randint(1, 6), random.randint(1, 6)
        print(f'You rolled {dice}!')
        return dice

    def turn(self, user, command):
        """
        Executes the command that is picked by the user.
        :param user: User object
        :param command: dictionary containing the command type
        :return:
        """
        self.lastCommand = command

        # if the user wants to roll the dice, move the user and print the cell type and name that the user has arrived
        if command['type'] == "roll":
            dice = self.get_random_dice()
            user.move(dice, len(self.cells), self.salary)
            name = getattr(self.cells[user.location], 'name', '')
            print(f'You have arrived {self.cells[user.location].type} {name}!')
            # return

        # if the user wants to bail out of jail, check if the user has a jail free card. If the user has a jail free card,
        # ask the user if they want to use it. If the user does not have a jail free card, call the pay_bail method of the
        # jail cell
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

        # user picked up a chance card that is either upgrade or downgrade
        elif command['type'] == "pickProp":

            # print all possible properties that the user can upgrade or downgrade
            for i, cell in enumerate(self.cells):
                if cell.type == 'property':
                    print(f'{i}: {cell["name"]}')

            # ask the user to select a property and apply the chance card to the property
            prop = int(input('Select possible property: (0,1,2...)\n'))
            self.cells[user.location].applyChanceCard([self.cells[prop]], user, self)

        # user picked up a chance card that is either color upgrade or color downgrade
        elif command['type'] == 'pickColor':

            # get all the colors of the properties that the user owns
            user_colors = set()
            for prop in user.properties:
                user_colors.add(prop.color)

            # print all possible colors that the user can upgrade or downgrade
            if len(user_colors) != 0:
                for i, color in enumerate(user_colors):
                    print(f'{i}: {color}')

                # ask the user to select a color and apply the chance card to the properties of the color
                prop = int(input('Select possible color to upgrade: (0,1,2...)\n'))
                color_props = self.getPropertiesByColor(list(user_colors)[prop])
                self.cells[user.location].applyChanceCard(color_props, user, self)

        # if the user is on a property cell and wants to buy the property, call the buyProperty method of the property cell
        elif command['type'] == "buy":
            self.cells[user.location].buyProperty(user)
            print(self.getuserstate(user))

        # if the user is on a property cell and wants to upgrade the property, call the upgrade method of the property cell
        elif command['type'] == "upgrade":
            self.cells[user.location].upgrade(self.upgrade, user)
            print(self.getuserstate(user))

        # if the user is on teleport cell and wants to teleport, ask the user to enter a destination and call the teleport
        # method of the teleport cell
        elif command['type'] == "teleport":
            destination = input(f'Enter your destination between 0 and {len(self.cells) - 1}:\n')
            self.cells[user.location].teleport(user, destination)


    def getPropertiesByColor(self, color):
        """
        Returns all the properties of the given color
        :param color: string
        :return: list of property cells
        """
        return list(filter(lambda x: x.color == color, self.cells))

    def start(self):
        """
        Method containing the main game loop.
        :return:
        """
        self.started = True
        while self.started:
            # find which user's turn it is and get the possible commands for that user
            user = self.determine_next_user()
            possible_commands = []

            # inserted a try except block to catch any bankruptcy exceptions
            try:
                possible_commands = self.get_possible_commands(user)
            except Exception as e:
                print(e)
                return
            finally:

                # if there are possible commands, notify the user and execute the selected command
                if len(possible_commands) != 0:
                    selected_command = user.notifyTurn(possible_commands)
                    self.turn(user, selected_command)
                    self.lastCommand = selected_command

                # if there are no possible commands, move the user to the end of the userTurn list
                else:
                    last_user = self.userTurn.pop(0)
                    self.userTurn.append(last_user)
                    self.lastCommand = None

                # at the end of each turn, call the callback functions of the users
                for callback in self.callbacks.values():
                    callback(self.getboardstate())

    def get_possible_commands(self, user):
        """
        Returns the possible commands for the given user
        :param user: User object
        :return: list of possible commands
        """
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
