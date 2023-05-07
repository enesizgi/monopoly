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
from threading import *
from TCPMessage import TCPNotification


# Main board class
class Board():
    def __init__(self, file, board_id):

        """
        Constructor for the board class. Takes in a json file and parses it to create the board.
        :param file: .json file containing the board information
        """

        self.users = {}  # holds all the users, used dictionary for easy access (key = user_id)
        self.cells = []  # holds all the cells
        self.started = False  # boolean to check if the game has started, is used in main game loop
        self.userTurn = []
        self.turn_changed = True
        self.first_roll = True
        self.id = board_id
        self.lock = RLock()
        self.condition = Condition(self.lock)
        self.ready_count = 0
        self.current_user = None

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

    def attach(self, user: User, callback=None, turncb=None):

        """
        Attaches a user to the board. This is called when a user joins the game.
        :param user:
        :param callback:
        :param turncb:
        :return:
        """
        self.users[user.id] = user
        user.attached_to = self.id
        self.userTurn.append(user.id)

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
        self.users.pop(user.id)
        user.attached_to = None

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

        return {
            'users': [user.get() for user in self.users.values()],
            'cells': [cell.getstate() for cell in self.cells],
            'started': self.started,
            'userTurn': self.userTurn,
            'salary': self.salary,
            'upgrade': self.upgrade,
            'teleport': self.teleport,
            'jailbail': self.jailbail,
            'tax': self.tax,
            'lottery': self.lottery,
        }

    def ready(self, user):
        """
        Sets the user's ready status to true and checks if all users are ready. If all users are ready, the game starts.
        :param user: User object
        :return:
        """
        user.ready = True
        user.budget = self.salary
        self.ready_count += 1
        if self.ready_count >= 2:
            self.started = True
            self.current_user = self.determine_next_user()
            self.add_to_message_queue(TCPNotification('notification', 'Game Started'))
            self.condition.notify_all()

    @classmethod
    def get_random_dice(cls):
        """
        Returns a random dice roll
        :return:
        """
        dice = random.randint(1, 6), random.randint(1, 6)
        return dice

    def add_to_message_queue(self, message):

        for user in self.users.values():
            user.append_message(message)

    def turn(self, user, command):
        """
        Executes the command that is picked by the user.
        :param user: User object
        :param command: dictionary containing the command type
        :return:
        """

        # if the user wants to roll the dice, move the user and print the cell type and name that the user has arrived
        if command['type'] == "roll":
            dice = self.get_random_dice()
            self.add_to_message_queue(TCPNotification("notification", f'{user.username} rolled {dice}!'))
            if user.inJail:
                if dice[0] == dice[1]:
                    user.inJail = False
                    user.jailTurns = 0
                else:
                    user.jailTurns += 1
                    if user.jailTurns == 3:
                        user.inJail = False
                        user.jailTurns = 0
                    else:
                        return

            user.move(dice, len(self.cells), self.salary)
            name = getattr(self.cells[user.location], 'name', '')

            self.add_to_message_queue(TCPNotification("notification",
                                                      f'{user.username} have arrived {self.cells[user.location].type} {name}!'))
            # return

        # if the user wants to bail out of jail, check if the user has a jail free card. If the user has a jail free
        # card, ask the user if they want to use it. If the user does not have a jail free card, call the pay_bail
        # method of the jail cell
        elif command['type'] == "bail":
            if user.hasJailFreeCard:
                answer = command["args"][0]
                if answer == 'y':
                    user.hasJailFreeCard = False
                    user.jailTurns = 0
                    user.inJail = False
            else:
                self.cells[user.location].pay_bail(user)

            self.turn_changed = False

        # user picked up a chance card that is either upgrade or downgrade
        elif command['type'] == "pickProp":

            # print all possible properties that the user can upgrade or downgrade

            try:
                prop = int(command['args'][0])
                upgradable_properties = list(map(lambda x: x.location, self.get_upgradable_properties()))
                if prop in upgradable_properties:
                    self.cells[user.location].applyChanceCard([self.cells[prop]], user, self)

            except Exception as e:
                user.append_message(TCPNotification('notification', 'Wrong arguments'))


            # ask the user to select a property and apply the chance card to the property


        # user picked up a chance card that is either color upgrade or color downgrade
        elif command['type'] == 'pickColor':

            # get all the colors of the properties that the user owns
            user_colors = set()
            for prop in user.properties:
                user_colors.add(prop.color)

            # print all possible colors that the user can upgrade or downgrade

                # ask the user to select a color and apply the chance card to the properties of the color
            try:
                prop = int(command["args"][0])
                color_props = self.get_properties_by_color(list(user_colors)[prop])
                self.cells[user.location].applyChanceCard(color_props, user, self)
            except Exception as e:
                print(e)

        # if the user is on a property cell and wants to buy the property, call the buyProperty method of the
        # property cell
        elif command['type'] == "buy":
            self.cells[user.location].buyProperty(user)
            print(self.getuserstate(user))

        # if the user is on a property cell and wants to upgrade the property, call the upgrade method of the property
        # cell
        elif command['type'] == "upgrade":
            self.cells[user.location].upgrade(self.upgrade, user)
            print(self.getuserstate(user))

        # if the user is on teleport cell and wants to teleport, ask the user to enter a destination and call the
        # teleport method of the teleport cell
        elif command['type'] == "teleport":
            possible_cells = self.cells[user.location].get_possible_cells_to_teleport(self, user)
            for i, cell in enumerate(possible_cells):
                print(f'{i}: {cell.name}')

            try:
                destination = int(command["args"][0])
                self.cells[user.location].teleport(user, destination)
                message = f'{user.username} is teleporting to {destination} for {self.cells[user.location].teleport_fee}.'
                self.add_to_message_queue(TCPNotification('notification', message))
                self.turn_changed = False
            except:
                user.append_message(TCPNotification('notification', 'Wrong arguments'))

    def get_properties_by_color(self, color):
        """
        Returns all the properties of the given color
        :param color: string
        :return: list of property cells
        """
        return list(filter(lambda x: x.type == 'property' and x.owner_id != -1 and x.color == color, self.cells))

    def get_property_state(self, iterable):
        return list(map(lambda x: x.getstate(),iterable))

    def get_upgradable_properties(self):
        """
        Returns all the properties that can be upgraded
        :return: list of property cells
        """
        return self.get_property_state(filter(lambda x: x.type == 'property' and x.owner_id != -1 and x.level != 4, self.cells))

    def get_downgradable_properties(self):
        """
        Returns all the properties that can be downgraded
        :return: list of property cells
        """
        return self.get_property_state(filter(lambda x: x.type == 'property' and x.owner_id != -1 and x.level != 0, self.cells))

    def get_color_properties(self, user):
        """
        Returns all the colors of the properties that the user owns
        :param user: User object
        :return: list of strings
        """
        user_colors = set()
        for prop in user.properties:
            user_colors.add(prop.color)

        return user_colors

    def get_possible_commands(self, user):
        """
        Returns the possible commands for the given user
        :param user: User object
        :return: list of possible commands
        """
        possible_commands = []

        # if the user gathers the turn from the previous user, he can roll the dice
        if self.turn_changed:

            # Append the roll command to the possible commands
            possible_commands.append({'type': 'roll'})
            self.turn_changed = False

            # if the user is in jail, he can roll the dice or pay the bail (if he has enough money) or use \
            # a jail free card
            if user.inJail:
                user.jailTurns += 1
                if user.jailTurns == 3:
                    user.inJail = False
                    user.jailTurns = 0
                else:
                    if user.budget > self.jailbail or user.hasJailFreeCard:
                        possible_commands.append({'type': 'bail'})

        # if the user still has the turn (after rolling the dice)
        else:

            # it is guaranteed that the user will give the turn to the next user after executing a command
            self.turn_changed = True

            # user lands on property cell
            if self.cells[user.location].type == "property":

                # if the property is not owned, the user can buy it if he has enough money
                if self.cells[user.location].owner_id == -1:
                    if user.budget > self.cells[user.location].price:
                        possible_commands.append({'type': 'buy'})
                        possible_commands.append({'type': 'skip'})

                # if the property is owned by the user, he can upgrade it if he has enough money
                elif self.cells[user.location].owner_id == user.id:
                    if user.budget > self.upgrade:
                        possible_commands.append({'type': 'upgrade'})
                        possible_commands.append({'type': 'skip'})

                # if the property is owned by another user, the user has to pay the rent
                else:
                    prop = self.cells[user.location]
                    prop.payRent(self.users[prop.owner_id], user)
                    message = f'{user.username} paid {prop.rents[prop.level]} to {self.users[prop.owner_id].username} for {prop.name}'
                    self.add_to_message_queue(TCPNotification('notification', message))

                    if user.budget < 0:
                        self.started = False
                        raise Exception("User {} is bankrupt".format(user.id))

            # user lands on teleport cell
            elif self.cells[user.location].type == "teleport":
                if user.budget > self.teleport:
                    possible_commands.append({
                        'type': 'teleport',
                        'cells': self.cells[user.location].get_possible_cells_to_teleport(self, user)
                    })
                    possible_commands.append({'type': 'skip'})

            # user lands on chance card cell
            elif self.cells[user.location].type == "chance":
                chance_cell = self.cells[user.location]

                # randomly pick a chance card
                chance_cell.getChanceCard()
                message = f'{user.username} picked this chance card: {chance_cell.card}!'
                self.add_to_message_queue(TCPNotification('notification', message))

                # if the card is upgrade or downgrade, the user can pick a suitable property to upgrade or downgrade
                if chance_cell.card == 'Upgrade':
                    upgradable_properties = self.get_upgradable_properties()
                    if len(upgradable_properties) != 0:
                        possible_commands.append({'type': 'pickProp', 'props': upgradable_properties})
                elif chance_cell.card == 'Downgrade':
                    downgradable_properties = self.get_downgradable_properties()
                    if len(downgradable_properties) != 0:
                        possible_commands.append({'type': 'pickProp', 'props': downgradable_properties})

                # if the card is color upgrade or downgrade, the user can pick a suitable color to upgrade or downgrade
                elif chance_cell.card == 'Color Upgrade' or chance_cell.card == 'Color Downgrade':
                    user_colors = self.get_color_properties(user)
                    if len(user_colors) != 0:
                        possible_commands.append({'type': 'pickColor', 'colors': user_colors})
                else:
                    chance_cell.applyChanceCard(None, user, self)

                    # in case the user is bankrupt after applying the chance card, raise an exception
                    if chance_cell.card == 'Tax':
                        if user.budget < 0:
                            self.started = False
                            raise Exception("User {} is bankrupt".format(user.id))

            # user lands on gotojail cell
            elif self.cells[user.location].type == "gotojail":
                self.cells[user.location].goto_jail(user, jail_location=self.jail_cell_index)

            # user lands on tax cell
            elif self.cells[user.location].type == "tax":
                tax_cell = self.cells[user.location]
                tax_cell.pay_tax(user)

                # in case the user is bankrupt after paying the tax, raise an exception
                if user.budget < 0:
                    self.started = False
                    raise Exception("User {} is bankrupt".format(user.id))

        return possible_commands

    def determine_next_user(self):
        """
        Determines which user's turn it is
        :return: User object
        """

        # if the turn is changed, the user who had the turn before is moved to the end of the queue
        if self.turn_changed and not self.first_roll:
            last_user = self.userTurn.pop(0)
            self.userTurn.append(last_user)

        self.first_roll = False
        return self.users[self.userTurn[0]]

    def getboardinfo(self):
        """
        Returns the board info
        :return: board info
        """
        return json.dumps(
            {'id': self.id, 'started': self.started, 'users': [user.get() for user in self.users.values()]})

    def __str__(self):
        return f'Board id:{self.id} {self.cells} {self.upgrade} {self.teleport} {self.jailbail} {self.tax} {self.lottery} {self.salary}'
