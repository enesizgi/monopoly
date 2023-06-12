import json
from threading import RLock

from TCPMessage import TCPNotification
from hashlib import sha256

player_positions = [
    {'x': 20, 'y': 80},
    {'x': 180, 'y': 80},
    {'x': 340, 'y': 80},
    {'x': 500, 'y': 80},
    {'x': 660, 'y': 80},
    {'x': 680, 'y': 240},
    {'x': 680, 'y': 400},
    {'x': 680, 'y': 560},
    {'x': 680, 'y': 720},
    {'x': 520, 'y': 720},
    {'x': 360, 'y': 720},
    {'x': 200, 'y': 720},
    {'x': 20, 'y': 720},
    {'x': 20, 'y': 560},
    {'x': 20, 'y': 400},
    {'x': 20, 'y': 240},
]


class User:
    """
    This class represents a user in the game.
    """

    def __init__(self, initial_budget: int = None, user_id: int = None, username=None, email=None, fullname=None,
                 passwd=None):

        # Game related
        self.id = user_id
        self.properties = []
        self.location = 0
        self.location_x = player_positions[0]['x']
        self.location_y = player_positions[0]['y']
        self.inJail = False
        self.jailTurns = 0
        self.hasJailFreeCard = False
        self.budget = initial_budget
        self.callback = None
        self.turncb = None
        self.ready = False
        self.attached_to = None
        self.message_queue = []
        self.lock = RLock()
        self.possible_commands = []
        self.current_command = ""

        # Authentication related
        self.username = username
        self.email = email
        self.fullname = fullname
        self.passwd = passwd

    def set_ready(self, ready):
        with self.lock:
            self.ready = ready

    # ready can be moved here

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

        with self.lock:
        # check if user is in jail and if he can get out of jail by rolling doubles
            if self.inJail and dice1 == dice2:
                self.jailTurns = 0
                self.inJail = False

            # check if user is passing start
            if new_location >= cell_count:
                self.budget += salary
                print(f'You passed start and earned {salary}!')
            self.location = new_location % cell_count
            self.location_x = player_positions[self.location]['x']
            self.location_y = player_positions[self.location]['y']

    def get(self):
        with self.lock:
            return self.to_json()

    def auth(self, plainpass: str):
        file = open('db.json', 'r')
        try:
            m = sha256()
            m.update(plainpass.encode())
            passwords = file.read()
            passwords = json.loads(passwords)
            if passwords[self.username] == m.hexdigest():
                file.close()
                return True
        except Exception as e:
            print(e)
        file.close()
        return False

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
        with self.lock:
            return {
                'id': self.id,
                'properties': [props.getstate() for props in self.properties],
                'username': self.username,
                # 'properties': self.properties,
                'location': self.location,
                'location_x': self.location_x,
                'location_y': self.location_y,
                'inJail': self.inJail,
                'jailTurns': self.jailTurns,
                'hasJailFreeCard': self.hasJailFreeCard,
                'budget': self.budget,
                'ready': self.ready
            }

    def append_message(self, message):
        with self.lock:
            try:
                if isinstance(message, TCPNotification):
                    self.message_queue.append(message.make_message())
                else:
                    self.message_queue.append(message)
            except:
                pass
    def __repr__(self):
        return self.get()
