class User:
    def __init__(self, initial_budget: int, user_id: int):
        self.id = user_id
        self.properties = []
        self.location = None
        self.inJail = False
        self.hasJailFreeCard = False
        self.budget = initial_budget

    def board_callback(self, board):
        print('board callback', board)
        pass
