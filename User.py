import json


class User:

    """
    This class represents a user in the game.
    """
    def __init__(self, initial_budget: int = None, user_id: int = None, username=None, email=None, fullname=None, passwd=None):

        # Game related
        self.id = user_id
        self.properties = []
        self.location = 0
        self.inJail = False
        self.jailTurns = 0
        self.hasJailFreeCard = False
        self.budget = initial_budget
        self.callback = None
        self.turncb = None
        self.ready = False
        self.attached_to = None

        # Authentication related
        self.username = username
        self.email = email
        self.fullname = fullname
        self.passwd = passwd

    #ready can be moved here

    def move(self, dice, cell_count, salary):
        """
        This method moves the user to the new location.
        :param dice: (int, int)
        :param cell_count: int
        :param salary: int
        :return:
        """
        dice1, dice2 = dice
        new_location = (self.location + dice1 + dice2)

        # check if user is in jail and if he can get out of jail by rolling doubles
        if self.inJail and dice1 == dice2:
            self.jailTurns = 0
            self.inJail = False

        # check if user is passing start
        if new_location > cell_count:
            self.budget += salary
            print(f'You passed start and earned {salary}!')
        self.location = new_location % cell_count

    def get(self):
        return self.to_json()

    def auth(self, plainpass):
        return True

    def checksession(self, token):
        pass

    def login(self):
        pass

    def logout(self):
        pass

    def update(self, ready=None, user_id=None, username=None, email=None, fullname=None, passwd=None):
        if ready:
            self.ready = ready
        if user_id:
            self.id = user_id
        if username:
            self.username = username
        if email:
            self.email = email
        if fullname:
            self.fullname = fullname
        if passwd:
            self.passwd = passwd

    def notifyTurn(self, commands):
        """
        This method notifies the user that it is his turn. User should select a command from the list of commands.
        :param commands:
        :return:
        """
        print(f'Turncb called for {self.username}\n')
        print('Commands:')
        for i, command in enumerate(commands):
            print(f'{i}: {command["type"]}')

        command = int(input("Select possible command (0,1,2...)\n"))

        return commands[command]

    def to_json(self):
        return {
            'id': self.id,
            'properties': [props.getstate() for props in self.properties],
            'username': self.username,
            # 'properties': self.properties,
            'location': self.location,
            'inJail': self.inJail,
            'jailTurns': self.jailTurns,
            'hasJailFreeCard': self.hasJailFreeCard,
            'budget': self.budget,
            'ready': self.ready
        }

    def __repr__(self):
        return self.get()
