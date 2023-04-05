from .Cell import Cell


class Tax(Cell):

    def __init__(self, location, tax):
        super().__init__(location)
        self.tax = tax

    def __str__(self):
        return f'Tax {self.location}'

    def pay_tax(self, user):
        user.budget -= self.tax
