from .Cell import Cell


class GotoJail(Cell):

    """
    This class represents a gotojail cell in the board.
    """

    def __init__(self, location, cell_type):
        super().__init__(location, cell_type)

    def __str__(self):
        return f'GotoJail {self.location}'

    def goto_jail(self, user, jail_location):
        """
        This method sends the user to jail.
        :param user: User object
        :param jail_location: Jail location index
        :return:
        """
        user.location = jail_location
        user.inJail = True

    def getstate(self):
        return {
            "location": self.location,
            "type": "GotoJail"
        }

