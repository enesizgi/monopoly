from cell.Cell import Cell


class Tax(Cell):

    """
    This class represents a tax cell in the board.
    """

    def __init__(self, location, tax, cell_type):
        super().__init__(location, cell_type)
        self.tax = tax
        self.name = 'Tax'

    def __str__(self):
        return f'Tax {self.location}'

    def pay_tax(self, user):
        """
        This method pays the tax to the user.
        :param user: User object
        :return:
        """
        user.budget -= self.tax

    def getstate(self):
        return {
            'location': self.location,
            'tax': self.tax,
            'type': 'Tax'
        }