import json


class User:
    def __init__(self, initial_budget: int, user_id: int, username=None, email=None, fullname=None, passwd=None):
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
        self.username = username
        self.email = email
        self.fullname = fullname
        self.passwd = passwd


    def board_callback(self, board):
        print('board callback', board)
        pass

    def move(self, dice, cell_count, salary):
        dice1, dice2 = dice
        new_location = (self.location + dice1 + dice2)
        if self.inJail and dice1 == dice2:
            self.jailTurns = 0
            self.inJail = False

        # check if user is passing start
        if new_location > cell_count:
            self.budget += salary
        self.location = new_location % cell_count

    def get(self):
        return json.dumps({
            'id': self.id,
            'properties': self.properties,
            'location': self.location,
            'inJail': self.inJail,
            'hasJailFreeCard': self.hasJailFreeCard,
            'budget': self.budget,
            'ready': self.ready
        })

    def auth(self, plainpass):
        pass

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
        print('Commands:')
        for i, command in enumerate(commands):
            print(f'{i}: {command["name"]}')

        command = int(input("Select possible command (0,1,2...)"))

        return command

