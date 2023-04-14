from .Cell import Cell


class Jail(Cell):

    """
    This class represents a jail cell in the board.
    """

    def __init__(self, location, jail_bail: int, cell_type):
        super().__init__(location, cell_type)
        self.jail_bail = jail_bail

    def __str__(self):
        return f'Jail {self.location}'

    def pay_bail(self, user):
        """
        This method pays the bail to the user.
        :param user:
        :return:
        """
        user.budget -= self.jail_bail
        user.inJail = False
        user.jailTurns = 0

    def getstate(self):
        return {
            'location': self.location,
            'jail_bail': self.jail_bail,
            'type': 'Jail'
        }
