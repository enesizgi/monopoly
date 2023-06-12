from cell.Cell import Cell


class Lottery(Cell):

    """
    This class represents a lottery cell in the board.
    """

    def __init__(self, location, lottery_fee, cell_type):
        super().__init__(location, cell_type)
        self.lottery_fee = lottery_fee

    def __str__(self):
        return f'Lottery {self.location}'

    def lottery(self, user):
        user.budget += self.lottery_fee

    def getstate(self):
        return {
            'location': self.location,
            'lottery_fee': self.lottery_fee,
            'type': 'Lottery'
        }
