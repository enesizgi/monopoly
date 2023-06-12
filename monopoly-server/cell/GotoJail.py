from cell.Cell import Cell
from User import player_positions

class GotoJail(Cell):

    """
    This class represents a gotojail cell in the board.
    """

    def __init__(self, location, cell_type):
        super().__init__(location, cell_type)
        self.name = 'GotoJail'

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
        user.location_x = player_positions[jail_location]['x']
        user.location_y = player_positions[jail_location]['y']
        user.inJail = True

    def getstate(self):
        return {
            "location": self.location,
            "type": "GotoJail"
        }

