class User:
    def __init__(self, initial_budget: int, user_id: int):
        self.id = user_id
        self.properties = []
        self.location = None
        self.inJail = False
        self.hasJailFreeCard = False
        self.budget = initial_budget
        self.callback = None
        self.turncb = None
        self.ready = False

    def board_callback(self, board):
        print('board callback', board)
        pass

    def move(self, dice, cell_count, salary):
        dice1, dice2 = dice
        new_location = (self.location + dice1 + dice2)
        if self.inJail and dice1 == dice2:
            self.inJail = False

        # check if user is passing start
        if new_location > cell_count:
            self.budget += salary
        self.location = new_location % cell_count

    def getState(self):
        return {
            'id': self.id,
            'properties': self.properties,
            'location': self.location,
            'inJail': self.inJail,
            'hasJailFreeCard': self.hasJailFreeCard,
            'budget': self.budget,
            'ready': self.ready
        }
