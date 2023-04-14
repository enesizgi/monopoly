from .Cell import Cell


class Teleport(Cell):

    """
    This class represents a teleport cell in the board.
    """

    def __init__(self, location, teleport_fee, cell_type):
        super().__init__(location, cell_type)
        self.teleport_fee = teleport_fee

    def __str__(self):
        return f'Teleport {self.location}'

    def teleport(self, user, destination):
        """
        This method teleports the user to the destination.
        :param user: User object
        :param destination: int
        :return:
        """
        print(f'{user.username} is teleporting to {destination} for {self.teleport_fee}.')
        user.location = destination
        user.budget -= self.teleport_fee

    def getstate(self):
        return {
            'location': self.location,
            'teleport_fee': self.teleport_fee,
            'type': 'Teleport'
        }

