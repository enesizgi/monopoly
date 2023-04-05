from Cell import Cell


class Lottery(Cell):

    def __init__(self, location, lottery_fee):
        super().__init__(location)
        self.lottery_fee = lottery_fee

    def __str__(self):
        return f'Lottery {self.location}'

    def lottery(self, user):
        user.budget += self.lottery_fee
