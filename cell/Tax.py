from .Cell import Cell


class Tax(Cell):

    def __init__(self, location, tax, cell_type):
        super().__init__(location, cell_type)
        self.tax = tax

    def __str__(self):
        return f'Tax {self.location}'

    def pay_tax(self, user):
        user.budget -= self.tax

    def getstate(self):
        return {
            'location': self.location,
            'tax': self.tax,
            'type': 'Tax'
        }